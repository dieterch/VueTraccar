import tomli, tomli_w
from pprint import pformat as pf, pprint as pp

cfgfile = "travels.toml"
cfgoutfile = "testout.toml"

with open(cfgfile, mode="rb") as fp:
    cfg = tomli.load(fp)


pp(cfg)


with open(cfgoutfile, mode="wb") as fp:
    tomli_w.dump(cfg, fp)
