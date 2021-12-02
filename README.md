# Gladier Kanzus Client




## Installing and Running

In order to run the Kanzus pipeline, two main steps need to be installed and checked. The remote resource used and the local resource at the beamline

### Remote resource

For the installation step

```bash
conda create -n gladier
conda activate gladier
pip install funcx
pip install funcx-endpoint
pip install pilot

funcx-endpoint start theta_local
funcx-endpoint start theta_queue
```

For configuring the funcx-endpoints please follow the instructions on.

```bash
conda activate gladier 
funcx-endpoint start theta_local
funcx-endpoint start theta_queue

```


### Beamline Install

```bash
conda create -n gladier
pip install gladier

git clone https://github.com/globus-gladier/gladier-kanzus

cd gladier-kanzus
pip install -e .
```

At this point you need to define where the data will be saved `$EXPERIMENT_FOLDER` and where the data will be processed on the remote resource `$REMOTE_FOLDER`

```bash
cd scripts
./kanzus_dev.py $EXPERIMENT_FOLDER --datafolder $REMOTE_FOLDER
```


