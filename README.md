# How to run:

First this needs to be the dir structre of your folder:

```bash=
/home/sgoswami/monobcntuples/local-samples/trf-workdir/SR/flattenedNTuples
??? bkg
?   ??? flat_tuple_ttbar.root
?   ??? flat_tuple_wlnu0.root
?   ??? flat_tuple_wlnu1.root
?   ??? flat_tuple_wlnu.root
?   ??? flat_tuple_znunu_600K.root
??? sig
?   ??? dm
?   ?   ??? flat_tuple_yy_1p0_qcd.root
?   ?   ??? flat_tuple_yy_1p5_qcd.root
?   ?   ??? flat_tuple_yy_2p5_qcd.root
?   ??? lq
?       ??? flat_tuple_lq_1p6TeV_merged_600K.root
?       ??? flat_tuple_lq_2p4TeV_merged_600K.root
?       ??? flat_tuple_lq_2TeV_merged_600K.root
```

Your `skeleton-config` and `python` script needs to reside here:
` /home/sgoswami/monobcntuples/local-samples/trf-workdir/`

Then run the following inside the trf inside the cvmfs environment after setting up `StatAnalysis`

`[/home/sgoswami/monobcntuples/local-samples/trf-workdir-bash] python3 run_all_signals.py`

The folders named `<fit_name>_fit` will appear on the top level directory (`trf-workdir`)
