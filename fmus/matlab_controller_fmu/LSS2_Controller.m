classdef LSS2_Controller < fmipputils.FMIAdapter

	properties
	
		tap_ = 0;

	end % properties


	methods
		
		function init( obj, currentCommunicationPoint )

			% Define inputs (of type real).
			inputVariableNames = { 'u_line1', 'u_line2', 'u_line3', 'u_line4', 'u_line5', 'u_line6', 'u_line7', 'vup', 'vlow' };
			obj.defineRealInputs( inputVariableNames );

			% Define outputs (of type int).
			outputVariableNames = { 'tap' };
			obj.defineIntegerOutputs( outputVariableNames );
			
			disp( 'FMI++ backend for co-simulation: INIT DONE.' );

		end % function init


		function doStep( obj, currentCommunicationPoint, communicationStepSize )
			
			syncTime = currentCommunicationPoint + communicationStepSize;

			if ( communicationStepSize ~= 0 ) % Update internal state of controller
				%disp('update state');
				;
			else
				%disp('iterate');
				obj.decideOnTap();
				obj.setIntegerOutputValues( obj.tap_ );
			end


		end % function doStep

		
		function decideOnTap( obj )

			% Read current input values.
			realInputValues = obj.getRealInputValues();
			u_line1 = realInputValues(1);
			u_line2 = realInputValues(2);
			u_line3 = realInputValues(3);
			u_line4 = realInputValues(4);
			u_line5 = realInputValues(5);
			u_line6 = realInputValues(6);
			u_line7 = realInputValues(7);
			vup = realInputValues(8);
			vlow = realInputValues(9);

			umin = min( [ u_line1 u_line2 u_line3 u_line4 u_line5 u_line6 u_line7 ] );
			umax = max( [ u_line1 u_line2 u_line3 u_line4 u_line5 u_line6 u_line7 ] );
			
			if ( umax > vup )
				obj.tap_ = obj.tap_ + 1;
			end
			
			if ( umin < vlow )
				obj.tap_ = obj.tap_ - 1;
			end
			
		end % function decideOnTap
		
	end % methods

end % classdef