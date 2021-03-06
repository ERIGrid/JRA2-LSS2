%% Debugging MATLAB code before FMU export
% Implemented MATLAB code can be tested and debugged before exporting it as
% an FMU for Co-Simulation. This can be done using the dedicated methods
% |debugSetRealInputValues|, |debugGetRealOutputValues|, etc. of class
% |fmipputils.FMIAdapter| to set/get the inputs/outputs/parameters.

%%
% When in debug mode, the interface used by external master algorithms is
% not activated. This will cause warnings like _"Warning: FMI++ export
% interface is not active."_. The following command mutes these warnings.
warning( 'off', 'all' );

%%
% Import the class implementing the controller.
import LSS2_Controller

%%
% Instantiate the controller.
test = LSS2_Controller();

test.init( 0. );

test.debugSetRealInputValues( [ 1.07, 0.99, 0.99, 0.99, 0.99, 0.99, 0.99, 1.05, 0.95 ] );

test.doStep( 0., 0. );

output = test.debugGetIntegerOutputValues()

test.doStep( 0., 100. );

test.debugSetRealInputValues( [ 1.01, 0.99, 0.91, 0.99, 0.93, 0.99, 0.99, 1.05, 0.95 ] );

test.doStep( 100., 0. );

output = test.debugGetIntegerOutputValues()

test.doStep( 100., 100. );

test.debugSetRealInputValues( [ 1.01, 0.99, 0.99, 0.99, 0.99, 0.99, 1.09, 1.05, 0.95 ] );

test.doStep( 200., 0. );

output = test.debugGetIntegerOutputValues()
