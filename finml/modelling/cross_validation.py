import numpy as np
import polars as pl 
from sklearn.metrics import log_loss, accuracy_score

def _get_purged_train_indices(event_times, test_times ):
    event_times = event_times.select(
        [pl.all(), pl.arange(0, pl.count()).alias("count_index")]
    )
    train_times = event_times.clone()
    for test_start,test_end in test_times.iterrows():
        overlap1 = event_times.filter((test_start<=pl.col("event_starts")) & (pl.col("event_starts") <= test_end))
        overlap2 = event_times.filter((test_start<=pl.col("event_ends")) & (pl.col("event_ends") <= test_end))
        overlap3 = event_times.filter((test_start>=pl.col("event_starts")) & (pl.col("event_ends") >= test_end))
        overlap = pl.concat([overlap1,overlap2,overlap3],how="vertical").unique()
        train_times = train_times.join(overlap,on ="event_ends",how ="anti")        
    return train_times.select("count_index").to_numpy().flatten()


def _get_embargo_times(bar_times, embargo_pct):
    if isinstance(bar_times,np.ndarray):
        bar_times = list(bar_times)
    elif isinstance(bar_times,pl.Series):
        bar_times = bar_times.to_list()
    
    step = 0 if bar_times is None else int(len(bar_times) * embargo_pct)
    if step == 0:
        res = pl.DataFrame({"start":bar_times,"end":bar_times})
    else:
        res = pl.concat([
            pl.DataFrame({"start":bar_times[:-step],"end":bar_times[step:]}),
            pl.DataFrame(
                {"start":bar_times[-step:],"end":[bar_times[-1] for i in range(step)]}
            )
        ],how="vertical")
    return res


def apply_purging_and_embargo(event_times, test_times, bar_times=None, embargo_pct=0.):
    if bar_times is not None:
        embargo_times = _get_embargo_times(bar_times, embargo_pct)
        adj_test_times = embargo_times.join(test_times,left_on = "start",right_on="end",how="inner").select(
            [pl.col("start_right").alias("start"),pl.col("end")]
        )
    else:
        adj_test_times = test_times
    train_indices = _get_purged_train_indices(event_times, adj_test_times)
    return train_indices



class PurgedKFold:

    def __init__(self, n_splits=3, embargo_pct=0.):
        
        self.n_splits = n_splits
        self.embargo_pct = embargo_pct

    def split(self, event_times):
        '''
        params: event_times: pl.DataFrame with two columns("start" and "end").
        '''
        num_obs = event_times.shape[0]
        indices = np.arange(num_obs)
        embargo = int(num_obs * self.embargo_pct)
        test_splits = [(i[0], i[-1] + 1) for i in np.array_split(indices, self.n_splits)]

        for i, j in test_splits:
            test_indices = indices[i:j]
            test_start_time = event_times[i.item(),"start"]
            train_1_indices = indices[(event_times.select("end") < test_start_time).to_numpy().flatten()]
            train_indices = train_1_indices

            test_end_time = event_times[test_indices,"end"].max()[0,"end"]
            train_2_start_idx = event_times.select("start").to_numpy().flatten().searchsorted(test_end_time, side='right') + 1
            if train_2_start_idx < num_obs:
                train_indices = np.concatenate((train_1_indices, indices[train_2_start_idx + embargo:]))

            yield train_indices, test_indices
            







