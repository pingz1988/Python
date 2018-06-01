# modified from official documentation

# -*- coding=utf-8 -*-
# !/usr/bin/env python

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

if __name__ == '__main__':
    # Creating a Series by passing a list of values, letting pandas create a default integer index:
    s = pd.Series([1, 3, 5, np.nan, 6, 8])
    print(s)

    # Creating a DataFrame by passing a numpy array, with a datetime index and labeled columns:
    dates = pd.date_range('20180102', periods=6)
    print(dates)

    df = pd.DataFrame(np.random.randn(6, 4), index=dates, columns=list(['aa', 'bb', 'cc', 'dd']))
    print("\ndf:\n", df)

    # Creating a DataFrame by passing a dict of objects that can be converted to series-like.
    df2 = pd.DataFrame({'A': 1,
                        'B': pd.Timestamp('20180102'),  # pd.date_range('20180102', periods=4) 这种形式也可以
                        'C': pd.Series(1, index=list(range(4)), dtype='float32'),
                        'D': np.array([3] * 4, dtype='int32'),
                        'E': pd.Categorical(["test", "train", "test", "train"]),
                        'F': 'foo'})
    print("\ndf2:\n", df2)

    # See the top & bottom rows of the frame
    print("\ndf.head(2):\n", df.head(2))       # 头2行
    print("\ndf.tail(3):\n", df.tail(3))       # 后3行

    # Display the index, columns, and the underlying numpy data
    print(df.index)
    print(df.columns)
    print(df.values)

    # Describe shows a quick statistic summary of your data
    print("\ndf.describe():\n", df.describe())

    # Sorting by an axis
    print("\ndf.sort_index():\n", df.sort_index(axis=1, ascending=False))

    # Sorting by values
    col = 'bb'
    if col in df.columns:
        print("\ndf.sort_values():\n", df.sort_values(by=col))

    # -----Selection by Label>>>
    # Selecting a single column, which yields a Series, equivalent to df.A
    col = 'aa'
    if col in df.columns:
        print("\ndf[col]:\n", df[col])

    # Selecting via [], which slices the rows.
    print("\ndf[0:3]:\n", df[0:3])

    print("\ndf['20180102':'20180104']:\n", df['20180102':'20180104'])

    # For getting a cross section using a label
    print("\ndf.loc[dates[0]]:\n", df.loc[dates[0]])

    # Selecting on a multi-axis by label
    print("\ndf.loc[:, ['aa', 'bb']]:\n", df.loc[:, ['aa', 'bb']])

    # Showing label slicing, both endpoints are included
    print("\ndf.loc['20180102':'20180104',['aa','bb']]:\n", df.loc['20180102':'20180104', ['aa', 'bb']])

    # For getting a scalar value
    print("\ndf.loc[dates[0],'aa']:\n", df.loc[dates[0], 'aa'])
    # For getting fast access to a scalar (equiv to the prior method)
    print("\ndf.at[dates[0],'aa']:\n", df.at[dates[0], 'aa'])
    # -----Selection by Label<<<

    # -----Selection by Position-----
    # Select via the position of the passed integers
    print("\ndf.iloc[3]:\n", df.iloc[3])
