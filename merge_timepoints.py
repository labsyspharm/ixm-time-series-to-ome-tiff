import itertools
import pathlib
import sys
import tifffile

in_path = pathlib.Path(sys.argv[1])
out_path = pathlib.Path(sys.argv[2])

if not out_path.exists():
    print(f"output path does not exist: {out_path}")
    sys.exit(1)

print("Scanning folder for TIFF files...")
tif_paths = in_path.glob("**/*.tif")
names = [
    [int(p.parent.name.split("_")[-1])] + p.name[:-40].split("_")[1:] + [p]
    for p in tif_paths
    if "thumb" not in p.name
]

def nkey(x):
    return x[1:3]

names = sorted(names, key=nkey)
nmap = {tuple(k): list(v) for k, v in itertools.groupby(names, key=nkey)}

print("Writing output OME-TIFFs")
for (well, site), entries in nmap.items():
    tiff_out_path = out_path / f"{well}_{site}.ome.tif"
    entries = sorted(entries)
    num_times = len(set(e[0] for e in entries))
    num_channels = len(set(e[3] for e in entries))
    plane0 = tifffile.imread(entries[0][4])
    shape = (num_times, num_channels) + plane0.shape
    plane_iter = (tifffile.imread(e[4]) for e in entries)
    shape_fmt = " x ".join(str(x) for x in shape)
    print(f"{well} {site} ({shape_fmt}) -> {tiff_out_path}")
    with tifffile.TiffWriter(tiff_out_path, bigtiff=True) as writer:
        writer.write(
            shape=shape ,
            dtype=plane0.dtype,
            data=plane_iter,
            metadata={"axes": "TCYX"},
        )
