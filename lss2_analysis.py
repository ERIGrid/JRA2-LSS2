import matplotlib.pyplot as plt
import pandas as pd
import sys

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

if len(sys.argv) > 1:
    storename = sys.argv[1]
else:
    storename = 'erigridstore.h5'

store = pd.HDFStore(storename)
df = store['Monitor']
store.close()
df2 = df.to_frame(False).unstack().dropna(axis=1)
df2.columns = df2.columns.map('.'.join)
df2.index.name = ""
df2 = df2.rename(columns=lambda x: '.'.join(x.split('.')[2:]))

c1 = [c for c in df2.columns if 'U_' in c ]

plt.figure(dpi=200, figsize = (5,3) )
ax = plt.axes()
ax.set_xlim( left = 0, right = 120 )
df2.plot(y=c1, ax=ax, lw=1, ls='--')
leg = ax.legend(ncol=1, loc='lower right')
plt.xlabel("simulation time in s")
plt.ylabel("voltage in p.u.")

plt.subplots_adjust( left = 0.15, right = 0.97, top = 0.99, bottom = 0.14 )
plt.show()