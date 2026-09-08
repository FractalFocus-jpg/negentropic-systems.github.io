import importlib.util
from pathlib import Path
import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import pandas as pd
import pytest
from sklearn.metrics import average_precision_score

p=Path(__file__).resolve().parents[1]/'analysis/audit.py'
if not p.exists():p=Path(__file__).resolve().parent/'audit.py'
spec=importlib.util.spec_from_file_location('audit',p);a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)

class Store:
    def __init__(self):self.data={};self.lock=threading.Lock()
    def create(self,path,value):
        with self.lock:
            if path in self.data:raise a.Consumed(path)
            self.data[path]=value

def claim():return {'analysis_id':a.ID}
def series():
    r=np.random.default_rng(41).normal(0,.01,170)
    return pd.Series(100*np.exp(np.cumsum(r)),index=pd.bdate_range('2023-08-01',periods=170))

@pytest.mark.parametrize('scores',[[.2,.2,.5,.8],[1,0,1,0],[1,1,1,1],[.1,.2,.3,.4]])
def test_ap_ties(scores):
    y=[0,1,1,0];assert a.ap(y,scores)==pytest.approx(average_precision_score(y,scores))

def test_target_exact_future_slice():
    close=series();f=a.features(close);t=60
    expected=close.pct_change().iloc[t+1:t+21].std(ddof=1)*np.sqrt(252)
    assert f.future_vol.iloc[t]==pytest.approx(expected)
    assert f.target_start.iloc[t]==close.index[t+1]
    assert f.target_end.iloc[t]==close.index[t+20]

def test_future_prices_do_not_change_past_features():
    c=series();mutated=c.copy();mutated.iloc[91:]*=1.8
    first=a.features(c);second=a.features(mutated)
    np.testing.assert_allclose(first[a.SCORES[:4]].iloc[49:91],second[a.SCORES[:4]].iloc[49:91])

def test_training_target_spill_is_excluded():
    train,test,_=a.split(a.features(series()))
    assert (train.target_end<a.TEST_START).all();assert (test.target_start>test.index).all()

def test_test_prices_do_not_change_training_threshold():
    c=series();modified=c.copy();modified.loc[modified.index>=a.TEST_START]*=1.1
    assert a.split(a.features(c))[2]==a.split(a.features(modified))[2]

@pytest.mark.parametrize('block',[20,40,60])
def test_circular_sampler(block):
    idx=a.circular_indices(529,block,np.random.default_rng(4));assert len(idx)==529
    assert idx.min()>=0 and idx.max()<529
    for i in range(0,529,block):assert np.all(np.diff(idx[i:i+block])%529==1)

def test_variance_filter():
    r=np.array([.1,.3,-.2,.4]);h=a.variance_path(r,.1,.2,.6,.5);manual=[.5]
    for x in r[:-1]:manual.append(.1+.2*x*x+.6*manual[-1])
    np.testing.assert_allclose(h,manual)

def test_multihorizon_forecast():
    h=2.;values=[h]
    for _ in range(19):h=.1+.9*h;values.append(h)
    assert float(a.forecast_mean_variance(2.,.1,.9))==pytest.approx(np.mean(values))

def test_reservation_precedes_calculation():
    s=Store()
    def calc():assert f'ledger/reservations/{a.ID}.json' in s.data;return {'terminal':'PASS'}
    a.reserved_execution(s,claim(),calc);assert len(s.data)==2

def test_duplicate_denied_before_callback():
    s=Store();calls=[]
    a.reserved_execution(s,claim(),lambda:(calls.append(1) or {'terminal':'PASS'}))
    with pytest.raises(a.Consumed):a.reserved_execution(s,claim(),lambda:calls.append(2))
    assert calls==[1]

def test_crash_after_reservation_stays_consumed():
    class Crash(BaseException):pass
    s=Store()
    with pytest.raises(Crash):a.reserved_execution(s,claim(),lambda:(_ for _ in ()).throw(Crash()))
    with pytest.raises(a.Consumed):a.reserved_execution(s,claim(),lambda:{'terminal':'PASS'})
    assert len(s.data)==1

def test_write_then_timeout_stays_consumed():
    class TimeoutStore(Store):
        def create(self,path,value):
            super().create(path,value)
            if '/reservations/' in path:raise TimeoutError('response lost after write')
    s=TimeoutStore();calls=[]
    with pytest.raises(TimeoutError):a.reserved_execution(s,claim(),lambda:calls.append(1))
    with pytest.raises(a.Consumed):a.reserved_execution(s,claim(),lambda:calls.append(2))
    assert calls==[]

def test_terminal_persistence_failure_does_not_reopen():
    class FailingStore(Store):
        def create(self,path,value):
            if '/terminals/' in path:raise TimeoutError('terminal network unavailable')
            super().create(path,value)
    s=FailingStore();calls=[]
    with pytest.raises(TimeoutError):a.reserved_execution(s,claim(),lambda:(calls.append(1) or {'terminal':'PASS'}))
    with pytest.raises(a.Consumed):a.reserved_execution(s,claim(),lambda:calls.append(2))
    assert calls==[1]

def test_calculation_error_has_one_terminal():
    s=Store()
    with pytest.raises(ValueError):a.reserved_execution(s,claim(),lambda:(_ for _ in ()).throw(ValueError('fixture')))
    assert len(s.data)==2
    assert s.data[f'ledger/terminals/{a.ID}.json']['terminal']=='ANALYSIS_ERROR_AFTER_RESERVATION'

def test_concurrent_claims_single_winner():
    s=Store();calls=[]
    def worker(_):
        try:a.reserved_execution(s,claim(),lambda:(calls.append(1) or {'terminal':'PASS'}));return 1
        except a.Consumed:return 0
    with ThreadPoolExecutor(max_workers=8) as pool:assert sum(pool.map(worker,range(24)))==1
    assert len(calls)==1

def test_no_overwrite_local_receipt(tmp_path):
    p=tmp_path/'receipt.json';a.exclusive_json(p,{'first':True});original=p.read_bytes()
    with pytest.raises(FileExistsError):a.exclusive_json(p,{'first':False})
    assert p.read_bytes()==original

def test_invalid_prices_rejected():
    c=series();c.iloc[80]=np.nan
    with pytest.raises(ValueError):a.features(c)

def test_non_github_executor_refused(monkeypatch):
    monkeypatch.setattr(a.sys,'argv',['audit.py','--execute']);monkeypatch.delenv('GITHUB_ACTIONS',raising=False)
    assert a.main()==73
