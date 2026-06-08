
import numpy as np

out_fname = "events/fid_10M_captures.npy"
fname_base = "fid_captures"

output = np.empty((0, 3))

for i in range(10):
    fpath = f"events/10M_files/{fname_base}_{i}.npy"
    print(i, fpath)

    chunk = np.load(fpath)

    output = np.vstack((output, chunk))

np.save(out_fname, output)

exit()
