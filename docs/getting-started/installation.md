# Installation

This quick tutorial explains the step to install `reactor-maker`

## Quick Start
### Installation 

```bash
git clone https://github.com/KitsuHokkaido/ReactorMaker.git
cd ReactorMaker

conda create -n reactor-maker-env
conda activate reactor-maker

pip install -e .

```

### Basic Usage 

Before executing any of this following command, don't forget to activate your salome environnement by this command : (if salome is in your PATH) 

```bash
salome context
```

#### Command Line

Simple example with required parameters

```bash
reactor-maker -rd 20 100 -cd 6 10 -m 2 
```

#### Gui 

```bash
reactor-maker-gui
```
