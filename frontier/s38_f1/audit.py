"""S38-F1: post-terminal diagnostics. Never executes the consumed V2.1 entrypoint."""
from __future__ import annotations
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen
import numpy as np
import pandas as pd
import scipy
from scipy.optimize import minimize
from scipy.signal import lfilter
from sklearn.metrics import average_precision_score, roc_auc_score
import sklearn

ID = 'KFIN-S38-F1-20260908-001'
REPO = 'FractalFocus-jpg/negentropic-systems.github.io'
CODE_BRANCH = 'audit/s38-f1-next-frontier'
LEDGER_BRANCH = 'audit/s38-f1-evidence'
DATA_HASH = '30c8b42de4a4cf47b1c67d5117740024ef3a94092df2a0eba0ee906b929d90fc'
PARENT = 'KFIN-V2_1-20260908-002'
SCORES = ['beta', 'beta_D', 'beta_over_rho', 'kappa', 'persistence']
COMPARATORS = ['beta', 'beta_D', 'beta_over_rho', 'persistence']
TEST_START = pd.Timestamp('2024-01-01')

class Consumed(RuntimeError):
    pass

class GitHubStore:
    """Create-only records on a dedicated branch, not a path-scoped security token."""
    def __init__(self, token: str):
        self.token = token

    def create(self, path: str, payload: dict) -> None:
        if path not in {f'ledger/reservations/{ID}.json', f'ledger/terminals/{ID}.json'}:
            raise ValueError('Path is outside the two declared record locations')
        content = (json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + '\n').encode()
        body = json.dumps({'message': f'{ID}: create {path}', 'branch': LEDGER_BRANCH,
                           'content': base64.b64encode(content).decode()}).encode()
        req = Request(f'https://api.github.com/repos/{REPO}/contents/{path}', data=body,
                      headers={'Authorization': f'Bearer {self.token}',
                               'Accept': 'application/vnd.github+json',
                               'X-GitHub-Api-Version': '2022-11-28',
                               'User-Agent': 'S38-F1-audit'}, method='PUT')
        try:
            with urlopen(req, timeout=30) as response:
                if response.status != 201:
                    raise RuntimeError('Create did not return HTTP 201; refusing execution')
                json.load(response)
        except HTTPError as exc:
            if exc.code in (409, 422):
                raise Consumed('Record exists or creation conflicts; fail closed, never overwrite') from exc
            raise RuntimeError(f'GitHub record creation failed: HTTP {exc.code}') from exc
        # A timeout or uncertain server outcome propagates: NEVER retry analysis.


def reserved_execution(store, claim: dict, calculate):
    """Reservation precedes callback; a crash leaves the identity consumed."""
    key = claim['analysis_id']
    store.create(f'ledger/reservations/{key}.json', claim)
    try:
        result = calculate()
    except Exception as exc:
        store.create(f'ledger/terminals/{key}.json', {
            'analysis_id': key, 'terminal': 'ANALYSIS_ERROR_AFTER_RESERVATION',
            'error_type': type(exc).__name__, 'error': str(exc), 'claim': claim})
        raise
    store.create(f'ledger/terminals/{key}.json', result)
    return result


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def exclusive_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as handle:
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write('\n'); handle.flush(); os.fsync(handle.fileno())


def features(close: pd.Series) -> pd.DataFrame:
    if not isinstance(close.index, pd.DatetimeIndex) or not close.index.is_unique or not close.index.is_monotonic_increasing:
        raise ValueError('Strict chronological, unique date index required')
    if not np.isfinite(close.to_numpy()).all() or (close <= 0).any():
        raise ValueError('All source prices must be finite and positive')
    r = close.pct_change(fill_method=None)
    out = pd.DataFrame({'returns': r}, index=close.index)
    out['beta'] = r.rolling(20).std(ddof=1) * np.sqrt(252)
    trend = close.rolling(50).mean()
    out['D'] = (close-trend).abs()/trend
    out['rho'] = 1-r.rolling(20).apply(lambda x: x.autocorr(lag=1)).abs()
    out['beta_D'] = out.beta * out.D
    out['beta_over_rho'] = out.beta/(out.rho+0.001)
    out['kappa'] = out.beta_D/(out.rho+0.001)
    out['future_vol'] = r.rolling(20).std(ddof=1).shift(-20)*np.sqrt(252)
    dates = pd.Series(close.index, index=close.index)
    out['target_start'] = dates.shift(-1)
    out['target_end'] = dates.shift(-20)
    return out


def split(frame: pd.DataFrame):
    required = ['beta','D','rho','beta_D','beta_over_rho','kappa','future_vol']
    clean = frame.dropna(subset=required).copy()
    if not np.isfinite(clean[required].to_numpy()).all():
        raise ValueError('Non-finite values beyond declared warm-up/tail filtering')
    train = clean.loc[(clean.index < TEST_START) & (clean.target_end < TEST_START)].copy()
    test = clean.loc[clean.index >= TEST_START].copy()
    if train.empty or test.empty:
        raise ValueError('Empty training/test data')
    threshold = float(train.future_vol.quantile(0.8))
    for f in (train,test):
        f['y'] = (f.future_vol > threshold).astype(int)
        f['persistence'] = (f.beta > threshold).astype(int)
    if test.y.nunique() != 2:
        raise ValueError('Both test classes required')
    return train,test,threshold


def ap(y, score) -> float:
    """Noninterpolated AP, grouping ties exactly as sklearn does."""
    y=np.asarray(y,dtype=int);score=np.asarray(score,dtype=float)
    if y.sum()==0:
        raise ValueError('AP not admitted without positives')
    order=np.argsort(-score, kind='stable'); yy=y[order]; ss=score[order]
    ends=np.r_[np.flatnonzero(np.diff(ss)!=0),len(ss)-1]
    positives=np.cumsum(yy)[ends]
    added=np.diff(np.r_[0,positives])
    return float(np.sum((added/y.sum()) * (positives/(ends+1))))


def circular_indices(n: int, block: int, rng) -> np.ndarray:
    starts=rng.integers(0,n,size=(n+block-1)//block)
    return ((starts[:,None]+np.arange(block))%n).ravel()[:n]


def variance_path(r: np.ndarray, omega: float, alpha: float, beta: float, initial: float) -> np.ndarray:
    innovations=np.r_[initial,omega+alpha*r[:-1]**2]
    return lfilter([1.0],[1.0,-beta],innovations)


def forecast_mean_variance(next_variance, omega: float, persistence: float, horizon: int=20):
    current=np.asarray(next_variance,dtype=float).copy();total=current.copy()
    for _ in range(1,horizon):
        current=omega+persistence*current;total+=current
    return total/horizon


def conventional_scores(close: pd.Series):
    r=(close.pct_change(fill_method=None).dropna()*100).astype(float)
    train=r.loc[r.index<TEST_START].to_numpy()
    initial=float(np.var(train,ddof=1))
    def objective(x):
        omega,alpha,beta=x
        if omega<=0 or alpha<0 or beta<0 or alpha+beta>=1:
            return 1e50
        h=variance_path(train,omega,alpha,beta,initial)
        if np.any(h<=0) or not np.isfinite(h).all():
            return 1e50
        return float(0.5*np.sum(np.log(h)+train**2/h))
    trials=[]
    for alpha,beta in [(0.05,0.90),(0.10,0.80),(0.15,0.80)]:
        fit=minimize(objective,[(1-alpha-beta)*initial,alpha,beta],method='SLSQP',
                     bounds=[(1e-10,max(10.,10*initial)),(0,0.999),(0,0.999)],
                     constraints=[{'type':'ineq','fun':lambda x:0.999999-x[1]-x[2]}],
                     options={'maxiter':1000,'ftol':1e-9})
        trials.append(fit)
    accepted=[x for x in trials if x.success and np.isfinite(x.fun) and x.fun<1e49]
    if not accepted:
        raise RuntimeError('No admissible GARCH training fit; no fallback/baseline shopping')
    fit=min(accepted,key=lambda x:x.fun);omega,alpha,beta=map(float,fit.x)
    h=variance_path(r.to_numpy(),omega,alpha,beta,initial)
    next_h=omega+alpha*r.to_numpy()**2+beta*h
    prediction=forecast_mean_variance(next_h,omega,alpha+beta)
    garch=pd.Series(np.sqrt(prediction*252)/100,index=r.index)
    ewma=np.empty(len(r));h_ewma=float(np.mean(train[:20]**2))
    for i,value in enumerate(r.to_numpy()):
        h_ewma=0.94*h_ewma+0.06*value**2;ewma[i]=h_ewma
    ewma=pd.Series(np.sqrt(ewma*252)/100,index=r.index)
    meta={'model':'Zero-mean Gaussian QMLE GARCH(1,1)', 'omega':omega,'alpha':alpha,'beta':beta,
          'training_end':str(r.loc[r.index<TEST_START].index[-1].date()),
          'training_observations':len(train),'fixed_parameters_during_test':True,
          'selected_by':'minimum TRAINING likelihood among three fixed optimizer initializations',
          'optimizer_successes':len(accepted), 'ewma_decay':0.94,
          'target_note':'Mean future conditional variance is a volatility-ranking proxy, not an exact forecast of centered sample SD.'}
    return garch,ewma,meta


def bootstrap(test: pd.DataFrame) -> dict:
    names=SCORES+['garch','ewma'];y=test.y.to_numpy();matrix=test[names].to_numpy()
    output={}
    for block in [20,40,60]:
        rng=np.random.default_rng(20260908+block);deltas=[];invalid=0
        for _ in range(5000):
            idx=circular_indices(len(y),block,rng);yy=y[idx]
            if yy.sum()==0 or yy.sum()==len(yy):
                invalid+=1;continue
            values=np.array([ap(yy,matrix[idx,j]) for j in range(len(names))])
            deltas.append(values[3]-values)
        arr=np.asarray(deltas)
        if len(arr)<100:
            output[str(block)]={'terminal':'DATA_INSUFFICIENT','valid':len(arr),'invalid':invalid};continue
        comparisons={}
        for name in COMPARATORS+['garch','ewma']:
            v=arr[:,names.index(name)]
            comparisons[name]={'delta_ap':ap(y,test.kappa)-ap(y,test[name]),
                'percentile_interval_95':np.quantile(v,[.025,.975]).tolist(),
                'bonferroni_interval_original_four':np.quantile(v,[.00625,.99375]).tolist() if name in COMPARATORS else None,
                'fraction_bootstrap_delta_positive':float(np.mean(v>0))}
        output[str(block)]={'replicates_attempted':5000,'valid':len(arr),'invalid':invalid,
             'block_length':block,'comparison_intervals':comparisons,
             'interpretation':'Paired conditional descriptive intervals; not selection-adjusted or prospective confidence.'}
    return output


def execute_analysis(root: Path, out: Path, claim: dict) -> dict:
    parent_path=root/'receipts'/f'{PARENT}.json'
    parent=json.loads(parent_path.read_text())
    close=pd.read_csv(root/'sp500.csv',index_col=0,parse_dates=True,skiprows=[1,2])['Close']
    frame=features(close);train,test,threshold=split(frame)
    if len(test)!=parent['counts']['test_rows'] or int(test.y.sum())!=parent['counts']['test_positive_targets']:
        raise RuntimeError('Parent row/target counts did not reconstruct')
    reconstructed={name:ap(test.y,test[name]) for name in SCORES}
    for name,value in reconstructed.items():
        if not np.isclose(value,parent['results'][name]['average_precision'],atol=1e-12,rtol=0):
            raise RuntimeError(f'Parent AP mismatch for {name}: {value}')
        if not np.isclose(value,average_precision_score(test.y,test[name]),atol=1e-12,rtol=0):
            raise RuntimeError('Independent AP implementation disagreement')
    if not np.isclose(threshold,parent['training_target_threshold'],atol=1e-12,rtol=0):
        raise RuntimeError('Parent threshold mismatch')
    garch,ewma,meta=conventional_scores(close)
    test['garch']=garch.reindex(test.index);test['ewma']=ewma.reindex(test.index)
    if not np.isfinite(test[SCORES+['garch','ewma']].to_numpy()).all():
        raise RuntimeError('Non-finite benchmark scores')
    point={name:{'average_precision':ap(test.y,test[name]),'roc_auc':float(roc_auc_score(test.y,test[name]))}
           for name in SCORES+['garch','ewma']}
    clusters=[];start=None
    for i,value in enumerate(test.y.to_numpy()):
        if value and start is None:start=i
        if start is not None and (not value or i==len(test)-1):
            end=i-1 if not value else i
            clusters.append({'start':str(test.index[start].date()),'end':str(test.index[end].date()),'rows':end-start+1})
            start=None
    intervals=bootstrap(test)
    primary=intervals['40']
    if primary.get('invalid',5000)>250:
        status='DATA_INSUFFICIENT_FOR_STABLE_BOOTSTRAP'
    elif all(primary['comparison_intervals'][c]['bonferroni_interval_original_four'][0]>0
             and primary['comparison_intervals'][c]['delta_ap']>=.02 for c in COMPARATORS):
        status='DESCRIPTIVE_ROBUSTNESS_CRITERION_MET__NOT_PROSPECTIVE_VALIDATION'
    else:
        status='UNCERTAINTY_NOT_RESOLVED__POINT_ESTIMATE_ONLY'
    result={'analysis_id':ID,'parent_id':PARENT,'terminal':status,'claim':claim,
        'analysis_class':'POST_TERMINAL_DIAGNOSTIC__SAME_OBSERVED_HOLDOUT__NON_INDEPENDENT',
        'parent_raw_aps_reconstructed':True,'parent_entrypoint_executed':False,
        'sample':{'train_rows':len(train),'test_rows':len(test),'positive_rows':int(test.y.sum()),
                  'test_start':str(test.index[0].date()),'test_end':str(test.index[-1].date()),
                  'positive_label_runs':clusters,'positive_runs_are_not_independent_events':True,
                  'adjacent_target_windows_share_returns':19},
        'point_metrics':point,'bootstrap':intervals,'conventional_baselines':meta,
        'environment':{'python':sys.version,'pandas':pd.__version__,'numpy':np.__version__,
                       'scipy':scipy.__version__,'sklearn':sklearn.__version__},
        'limitations':['Same previously inspected data: not a new blind confirmatory test.',
          'Bootstrap conditions on realized scores and fitted model; does not account for model selection or training-parameter uncertainty.',
          'Circular blocks assume adequate within-period stationarity; 20/40/60 sensitivity is not a proof of coverage.',
          'Disjoint feature/target returns do not make adjacent targets independent.',
          'No causal, trading-profit, medical, physical, universal-kappa or autonomy claim.',
          'V2.1 raw numbers preserved; final pre-merge reservation finding was unresolved. Fully-cleared confirmatory review claim withdrawn.']}
    out.mkdir(parents=True,exist_ok=True)
    with (out/'row_scores.csv').open('x',encoding='utf-8') as handle:
        test.to_csv(handle,index_label='feature_date')
    exclusive_json(out/'receipt.json',result)
    return result


def main() -> int:
    if sys.argv[1:]!=['--execute']:
        print('Explicit --execute is required; imports/tests do not execute the experiment.',file=sys.stderr);return 2
    expected={'GITHUB_ACTIONS':'true','GITHUB_REPOSITORY':REPO,'GITHUB_EVENT_NAME':'push',
              'GITHUB_REF':f'refs/heads/{CODE_BRANCH}','GITHUB_RUN_ATTEMPT':'1',
              'GITHUB_WORKFLOW_REF':f'{REPO}/.github/workflows/s38-f1-audit.yml@refs/heads/{CODE_BRANCH}'}
    if any(os.getenv(k)!=v for k,v in expected.items()) or not os.getenv('GITHUB_TOKEN') or not os.getenv('GITHUB_RUN_ID'):
        print('EXECUTOR_CONTEXT_REFUSED',file=sys.stderr);return 73
    root=Path(__file__).resolve().parents[2];here=Path(__file__).resolve().parent;out=root/'s38-f1-output'
    try:
        if digest(root/'sp500.csv')!=DATA_HASH:
            raise ValueError('Source dataset hash mismatch')
        claim={'analysis_id':ID,'status':'RESERVED_BEFORE_ANALYSIS','github_run_id':os.environ['GITHUB_RUN_ID'],
               'github_sha':os.environ['GITHUB_SHA'],'data_sha256':DATA_HASH,
               'protocol_sha256':digest(here/'PROTOCOL.md'),'script_sha256':digest(Path(__file__)),
               'parent_receipt_sha256':digest(root/'receipts'/f'{PARENT}.json')}
        result=reserved_execution(GitHubStore(os.environ['GITHUB_TOKEN']),claim,lambda:execute_analysis(root,out,claim))
        print(json.dumps(result,indent=2,sort_keys=True));return 0
    except Consumed:
        print('IDENTITY_CONSUMED_OR_CONFLICT__NO_ANALYSIS',file=sys.stderr);return 73
    except Exception as exc:
        print(f'FAIL_CLOSED: {type(exc).__name__}: {exc}',file=sys.stderr);return 2

if __name__=='__main__':
    raise SystemExit(main())
