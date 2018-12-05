[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.1934908.svg)](https://doi.org/10.5281/zenodo.1934908)

# ERIGrid JRA2: Test case LSS2 mosaik implementation

A detailed description of test case LSS2 can be found in [ERIGrid deliverable D-JRA2.3](https://erigrid.eu/dissemination/).
In the following, a step-by-step instruction on how to run the LSS2 co-simulation is provided as well as a brief description of the simulation components.


## Prerequisites (Windows)

 - **Python** (test with Python 3.6.4 32-bit)
 - **PowerFactory** (tested with PowerFactory 2017 SP5 x86) and the [**FMI++ PowerFactory FMU Export Utility**](https://sourceforge.net/projects/powerfactory-fmu/)
 - **MATLAB** (tested with MATLAB R2015b 32-bit) and the [**FMI++ MATLAB Toolbox for Windows**](https://sourceforge.net/projects/matlab-fmu/)
 - **ns-3** (installed in [Cygwin](https://www.cygwin.com/) environment, see documentation for ns-3 module fmi-export) with the extra modules [**fmi-export and fmu-examples**](https://erigrid.github.io/ns3-fmi-export/)

**ATTENTION**: The co-simulation toolchain needs to be completely in either 32-bit or 64-bit.
For LSS2 it was decided to use consistently **32-bit** for Windows setups.
Therefore, be sure to install **32-bit versions of all tools** (Python, PowerFactory, MATLAB, Cygwin)!


## Installation (Windows)

1. install all the tool listed in the prerequisites above (including the FMI-compliant interfaces)

2. in the Windows command line, install required Python packages via *pip* by running:
```
      pip install -r requirements.txt
```

3. in the Cygwin terminal, install required Python packages using *pip* (see details below)

4. create the FMUs (see details below)


### Install Cygwin Python packages

It is recommended to install everything into a virtual Python environment called *lss2*:
```
   pip2 install virtualenv virtualenvwrapper
   source /usr/bin/virtualenvwrapper.sh
   mkvirtualenv lss2
   pip2 install mosaik_api
```

**NOTE**:
It is not necessarily required to create this virtual Python environment.
However, if you prefer not to use one, you have to edit file *lss2_comm_ns3_fmu.sh* accordingly.


### Creating the MATLAB FMU

- open MATLAB and go to subfolder *fmus\matlab_controller_fmu*
- run MATLAB script *create_fmu.m*
- copy the resulting FMU to subfolder *fmus*


### Creating the PowerFactory FMU

- go to subfolder *fmus\pf_network_fmu*
- adapt batch script *create_fmu.bat* to fit your installation (path to FMI++ PowerFactory FMU Export Utility)
- run batch script *create_fmu.bat* (e.g., double-click it)
- copy the resulting FMU to subfolder *fmus*


### Creating the ns-3 FMU

- open a Cygwin terminal and go to subfolder *fmus\ns3_comm_fmu*
- adapt shell script *create_fmu.sh* to fit your installation (path to ns-3 installation)
- run shell script *create_fmu.sh*
- copy the resulting FMU to subfolder *fmus*


## Running the simulation (Windows)

There are two scenarios included here:

The first scenario uses FMUs on a Windows PC. For this scenario, DIgSILENT PowerFactory, MATLAB and ns-3 need to be installed and the associated FMUs have to be available (see above).

Because the ns-3 FMU has to be executed in a Cygwin environment, mosaik has to know the path to Cygwin's terminal application (*bash.exe*). For this reason, edit attribute *BASH_PATH* to point to *bash.exe* (beginning of file *lss2_scenario_fmu.py*).

For both scenarios, the time resolution of the simulation can be specified via parameter MT_PER_SEC, which defines the number of mosaik time steps per second (simulation time).

Once this is done, run the full LSS2 scenario with this command:
```
   set CHERE_INVOKING=1
   python lss2_scenario_fmu.py
```

It is also possible to run variations of the scenario, for instance by changing ns-3's random generator seed and the number of dummy devices:
```
   set CHERE_INVOKING=1
   python lss2_scenario_fmu.py --random_seed=1234 --n_devices=20
```

The second scenario does not include a communication network simulator. It is meant as a reference scenarion with "ideal" communication.
```
   python lss2_scenario_nocomm_fmu.py
```

Results from the simulations are stored in *erigridstore.h5* and can be plotted using:
```
   python lss2_analysis.py
```


## Brief description of component functionality


### LSS2PeriodicController

For the voltage controller a simple rule-based control algorithm is used, which periodically calculates tap position set-points for the OLTC transformer depending on the smart meter voltage measurements (*u_line1*, *u_line2*, *u_line3*, *u_line4*, *u_line5*, *u_line6*, *u_line7*).
This controller runs separately from the transformer and the smart meters, to which it is connected through the communication networks (both Wi-Fi and Ethernet).
The controller actuation is synchronized with the smart meters, i.e., it is always actuated directly after the smart meters send their data (but delayed by a short amount of time).

This implementation is intended to use an FMU that internally runs a control algorithm implemented in MATLAB.


### LSS2PowerSystem

A large radial low voltage distribution network with an OLTC MV/LV transformer has been chosen as power system.
It has been adapted from the [Kerber network 'Extrem Vorstadtnetz Kabel_d Typ II'] and is large in terms of connected loads and geographical size compared to typical low voltage distribution networks.
The tap changer is configured such that switching from one tap position to the next decreases (step up) or increases (step down) the voltage level at the LV side by 2,5%.

Towards the end of each feeder a smart meter is located, respectively.
These meters send measurement data (local voltage level) in regular intervals to the voltage controller via a wireless local network.
The sending of the data is synchronized among these smart meters, i.e., they all send their data at the same time.

This implementation is intended to use an FMU that internally uses PowerFactory.


### LSS2CommNetwork

For the purpose of this test case, each smart meter is connected to a wireless local network (Wi-Fi, networking standard 802.11ac, coding scheme index 3, and short guard interval disabled).
In addition to the smart meters, several other (unrelated) devices are connected to the same wireless local networks, which use the wireless local networks simultaneously to the smart meters.
Furthermore, each of these local networks has another additional Wi-Fi network close to it, transmitting at the same frequency and causing co-channel interference (frequency channel: 5180 Mhz, channel width: 40 Mhz).

In order to observe the impact of the co-channel interference, the additional Wi-Fi networks overload the frequency by sending packets at very small intervals (in the order of 10μs) with a packet size of 972 bytes.
Wireless conversations are managed using CSMA/CA (Carrier-sense multiple access with collision avoidance) and every station is sending frames only when the medium is idle.
As the smart meter’s local network is congested due to the overload from the additional Wi-Fi network, the shared channel is always busy.
This results in augmented waiting times and more packet collisions, reducing the performance of the smart meter’s local network significantly.
In addition, an Ethernet network (bandwidth: 100 Mbps, channel delay: 6560 ns) connects the Wi-Fi networks to the voltage controller and the OLTC.

This implementation is intended to use an FMU that internally runs ns-3 simulations.
Please note that ns-3 is being developed for Linux.
However, on Windows ns-3 can be run in a Cygwin environment.
And FMUs using ns-3 also have to be executed on Windows within a Cygwin environment.
Therefore, when using the LSS2CommNetwork component, mosaik starts a Cygwin session (*bash.exe*) in which it runs and connects to the client component (with the help of shell script *lss2_comm_ns3_fmu.sh*).


### PeriodicSender

Connecting *in* to a continuous time component will periodically raise *out* from None to the value of *in*.
This raising happens every *period* time steps, starting at *start_time*.


### Collector

Polls connected components every *timestep* mosaiktimes, saves results into the specified HDFstore.


## Troubleshooting

**Error message**:
```
/usr/bin/bash: ./lss2_comm_ns3_fmu.sh: No such file or directory
ERROR: Simulator "CommSim" did not connect to mosaik in time.
Mosaik terminating
```

**Solution**: You forgot to set variable `CHERE_INVOKING` before running mosaik.
```
   set CHERE_INVOKING=1
```
