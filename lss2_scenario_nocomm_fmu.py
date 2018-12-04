import mosaik
import mosaik.util
import os
import argparse
from pathlib import Path
from datetime import *

# Simulation stop time and scaling factor.
MT_PER_SEC = 10 # N ticks of mosaik time = 1 second
STOP = 120 * MT_PER_SEC # 2 minutes

# FMU repository.
FMU_DIR = os.path.abspath( os.path.join( os.path.dirname( __file__ ), 'fmus' ) )

# Define routing of voltage measurements and signals.
SIGNAL_TABLE = {
    'U_1_60': 'u_line1',
    'U_2_32': 'u_line2',
    'U_3_32': 'u_line3',
    'U_4_19': 'u_line4',
    'U_5_15': 'u_line5',
    'U_6_15': 'u_line6',
    'U_7_10': 'u_line7',
    }

# Sim config.
SIM_CONFIG = {
        'LoadFlowSim':{
            'python': 'lss2_powersystem_pf_fmu:LSS2PowerSystem'
        },
        'ControllerSim':{
            'python': 'lss2_periodic_controller_matlab_fmu:LSS2PeriodicController'
        },
        'PeriodicSender':{
            'python': 'periodic_sender:PeriodicSender',
        },
        'Collector':{
            'python': 'collector:Collector',
        }
    }


def main():

    parser = argparse.ArgumentParser(description='Run a LSS2 simulation')
    parser.add_argument( '--ctrl_dead_time', type=float, help='controller deadtime in seconds', default=2 )
    parser.add_argument( '--ctrl_phase_shift', type=float, help='time difference in seconds between sending voltage readings and computing new controller set points', default=1 )
    parser.add_argument( '--output_file', type=str, help='output file name', default='erigridstore.h5' )
    args = parser.parse_args()
    print( 'Starting simulation with args: {0}'.format( vars( args ) ) )

    world = mosaik.World( SIM_CONFIG )
    create_scenario( world, args )
    world.run( until=STOP )


def create_scenario( world, args ):

    # Periodic senders for voltage readings.
    sender_sim = world.start( 'PeriodicSender', verbose=False )
    senders = {
        v: sender_sim.PeriodicSender( period=60.*MT_PER_SEC ) for ( v, _ ) in SIGNAL_TABLE.items()
        }

    # Simulator for power system.
    loadflow_sim = world.start( 'LoadFlowSim',
        work_dir=FMU_DIR, model_name='LSS2_PowerSystem', instance_name='LoadFlow1',
        start_time=0, stop_time=STOP, stop_time_defined=True,
        step_size=1*MT_PER_SEC, seconds_per_mosaik_timestep=1/MT_PER_SEC, verbose=False )
    loadflow = loadflow_sim.LSS2PowerSystem.create(1)[0]

    # Simulator for controller.
    ctrl_sim = world.start( 'ControllerSim',
        work_dir=FMU_DIR, model_name='LSS2_Controller', instance_name='Controller1',
        start_time=0, stop_time=STOP, stop_time_defined=True,
        dead_time=args.ctrl_dead_time, seconds_per_mosaik_timestep=1./MT_PER_SEC, verbose=True )
    ctrl = ctrl_sim.LSS2PeriodicController.create(1, period=60., phase_shift=args.ctrl_phase_shift)[0]

    for voltage, signal in SIGNAL_TABLE.items():
        world.connect( loadflow, senders[voltage], ( voltage, 'in' ) )
        world.connect( senders[voltage], ctrl, ( 'out', signal ) )
        
    # Connect output from controller to OLTC.
    world.connect( ctrl, loadflow, ( 'tap', 'tap' ), time_shifted=True, initial_data={ 'tap': 0 } )

    # Collect results.
    collector = world.start( 'Collector',
        step_size=MT_PER_SEC, seconds_per_mosaik_timestep=1./MT_PER_SEC, print_results=False,
        h5_storename=args.output_file, h5_panelname='Monitor' )
    monitor = collector.Monitor()

    for voltage, signal in SIGNAL_TABLE.items():
        world.connect( loadflow, monitor, voltage )
        world.connect( senders[voltage], monitor, 'out' )
    world.connect( loadflow, monitor, 'current_tap' )


if __name__ == '__main__':
    sim_start_time = datetime.now()

    # Run the simulation.
    main()

    delta_sim_time = datetime.now() - sim_start_time
    print( 'simulation took {} seconds'.format( delta_sim_time.total_seconds() ) )
