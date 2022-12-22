import pandas as pd

def _snap_filter(df): 
  """
  helper function for groupby call. 
  returns pd.DataFrame containing a boolean for each frame that is True if ball was already snapped in that play
  """
  if "ball_snap" in df.event.unique():
    frame = df.loc[df.event=='ball_snap', "frameId"].iat[0]
    df["is_snapped"] = df.frameId.ge(frame)

    return df.groupby("frameId").agg({"is_snapped":"max"})

def add_snapped_filter_col(df): 
  """
  adds a column boolean called 'is_snapped' to a pd.DataFrame
  """
  snap_df = df[['gameId', 'playId', 'nflId', 'frameId', 'event']].groupby(['gameId', 'playId']).progress_apply(_snap_filter).reset_index()
  if "is_snapped" in df.columns:
    df = df.drop(columns="is_snapped") # easiest way codewise, else merge will rename cols
  df = pd.merge(df, snap_df[["gameId", "playId", "frameId", "is_snapped"]], on=["gameId", "playId", "frameId"])
  return df
