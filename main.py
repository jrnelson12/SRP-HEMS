from HEMS_data import HEMSData
data = HEMSData()
import math
import Dispatch
from Input_data import inputs_data
class HEMS():
    def __init__(self, *args, **kwargs):
        self.data = HEMSData()
def main():
    #Read in data
    data.set_input(*inputs_data())

    #Lists to store outputs
    PVPowerOut =[]
    IPowerOut =[]
    BatteryPower =[]
    GridPowerNet =[]
    BatteryCurrentCapacity =[]
    BatterySOC =[]

    #List to store inputs
    Day = []
    Hour = []
    DNI = []
    Load = []
    for hour in range(len(data.input.LocalTime)):
        #Simulate dispatch

        dispatch_result = Dispatch.Dispatch(*data.prep_for_dispatch(hour))
        data.set_dispatch_results(*dispatch_result)

        print (data.output.PVPowerOut, data.output.IPowerOut, data.output.BatteryPower, data.output.GridPowerNet,
                   data.input.BatteryCurrentCapacity, data.output.BatterySOC)

        # Changing from float to string
        data.to_string(hour)

        # Recording each timestep in list
        Day.append(data.input.DayOfYear[hour])
        Hour.append(data.input.LocalTime[hour])
        DNI.append(data.input.DNI[hour])
        Load.append(data.input.LoadUncontrollablePower[hour])
        PVPowerOut.append(data.output.PVPowerOut)
        IPowerOut.append(data.output.IPowerOut)
        BatteryPower.append(data.output.BatteryPower)
        GridPowerNet.append(data.output.GridPowerNet)
        BatteryCurrentCapacity.append(data.output.BatteryCurrentCapacity)
        BatterySOC.append(data.output.BatterySOC)

    # Writing to csv file
    f = open('HEMSOutputWeek1.csv', 'w')
    for z in range(len(data.input.LocalTime)):
        f.write(Day[z] + ',')
        f.write(Hour[z] + ',')
        f.write(DNI[z] + ',')
        f.write(Load[z] + ',')
        f.write(PVPowerOut[z] + ',')
        f.write(IPowerOut[z] + ',')
        f.write(BatteryPower[z] + ',')
        f.write(GridPowerNet[z] + ',')
        f.write(BatteryCurrentCapacity[z] + ',')
        f.write(BatterySOC[z])
        f.write('\n')
    f.close()
if __name__ == '__main__':
    main()
