class HEMSData():
    def __init__(self, *args, **kwargs):
        self.input = HEMSDataInput()
        self.output = HEMSDataOutput()

    def set_input(self, day, hour, dfi, dni, ghr, ambtemp, KT, gridPrice, controllableLoad, uncontrollableLoad):
        self.input.DayOfYear = day
        self.input.LocalTime = hour
        self.input.DFI = dfi
        self.input.DNI = dni
        self.input.GlobalHorizontalRadiation = ghr
        self.input.AmbientTemp = ambtemp
        self.input.ClearnessIndex = KT
        self.input.GridEnergyCost = gridPrice
        self.input.LoadControllablePower = controllableLoad
        self.input.LoadUncontrollablePower = uncontrollableLoad

    def prep_for_dispatch(self, hour):
        return self.input.EnergySystemType,self.input.LoadControllablePower[hour], self.input.LoadCurtailPercent,\
            self.input.LoadUncontrollablePower[hour], self.input.DayOfYear[hour], self.input.LocalTime[hour],\
            self.input.TimeZone, self.input.Longitude, self.input.Latitude, self.input.PVSlope,\
            self.input.GlobalHorizontalRadiation[hour], self.input.ClearnessIndex[hour], self.input.DNI[hour],\
            self.input.TimeStepHourlyFraction, self.input.DFI[hour], self.input.GroundReflectance,\
            self.input.Inverterefficeincy, self.input.PVcapacity, self.input.Invertercapacity,\
            self.input.StartTOU, self.input.StopTOU, self.input.BatteryCurrentCapacity,\
            self.input.BatteryNominalCapacity, self.input.BatteryMinCapacityAsFraction,\
            self.input.BatteryChargeEff, self.input.BatteryDischargeEff, self.input.BatteryMaxCRate, self.input.BatteryVoltageNominal

    def set_dispatch_results(self, pvPowerOut, iPowerOut, batteryPower, gridPowerNet, batteryCurrentCapacity, batterySOC):
        self.output.PVPowerOut = pvPowerOut
        self.output.IPowerOut = iPowerOut
        self.output.BatteryPower = batteryPower
        self.output.GridPowerNet = gridPowerNet
        self.input.BatteryCurrentCapacity = batteryCurrentCapacity
        self.output.BatterySOC = batterySOC

    def to_string(self, hour):
        #Outputs
        self.output.PVPowerOut = str(self.output.PVPowerOut)
        self.output.IPowerOut = str(self.output.IPowerOut)
        self.output.BatteryPower = str(self.output.BatteryPower)
        self.output.GridPowerNet = str(self.output.GridPowerNet)
        self.output.BatteryCurrentCapacity = str(self.input.BatteryCurrentCapacity)
        self.output.BatterySOC = str(self.output.BatterySOC)

        #Inputs
        self.input.DayOfYear[hour] = str(self.input.DayOfYear[hour])
        self.input.LocalTime[hour] = str(self.input.LocalTime[hour])
        self.input.DNI[hour] = str(self.input.DNI[hour])
        self.input.LoadUncontrollablePower[hour] = str(self.input.LoadUncontrollablePower[hour])

class HEMSDataInput():
    def __init__(self, *args, **kwargs):

        #Environmental Data
        self.AmbientTemp = []  # Ambient Temperature in [K]
        self.GlobalHorizontalRadiation = []      # Global Horizontal Radiation [W/m2]
        self.DNI = []   #Direct Normal Irradiance [W/m2]
        self.DFI = []   #Diffuse Horizontal Irradiance [W/m2]
        self.LocalTime = []   # Hour of the day 1 through 24
        self.DayOfYear = []  # Day of the year
        self.ClearnessIndex = []  # Clearness Index
        self.TimeStepHourlyFraction = 1
        self.GroundReflectance = 0 # Ground Reflectance

        # Site Specific Data
        self.Elevation = 331  # Building elevation in [m]
        self.Latitude = 33  # Latitude of the building location
        self.Longitude = -112  # Longitude of the building location
        self.TimeZone = -7  # Time zone away from GMT (negative for west poistive for east)
        self.EnergySystemType = 'solarPV & & inverter && battery'   #Type of energy system to be controlled possible loads,
        # solarPV && inverter, solarPV && inverter && battery
        self.StartTOU = 12  #Hour of day that TOU starts
        self.StopTOU = 20   #Hour of day that TOU stops


        #Energy Asset

        #Solar PV
        self.PVcapacity = 5 #kW size of PV array
        self.PVArea = 100 #m2 Area of PV array
        self.PVperformance = 0.9 #Performance or efficiency of PV array
        self.PVOrientation = 180 #PV array Azimuth angle (South Ref = 180)
        self.PVSlope = 33 #PV array Tilt andle (Perpendicular to ground = 0)

        #Inverter
        self.Inverterefficeincy = 0.9 #DC to AC conversion efficeincy
        self.Invertercapacity = 5 #kW size of Inverter

        #Grid
        self.GridEnergyCost = [] #$/kWh energy price for current hour
        #self.GridDemandCharge = 9 #$/kW demand charge for month
        self.GridNetMeter = 0.3 #$/kWh price paid for sending energy to grid

        #Battery
        self.BatteryPower = 5 #kW power has positive convention as output -- power output (+) or power to charge (-)
        self.BatteryChargeEff = 0.9 #Charging Efficeicny (Must take into account efficiecny of AC/DC and charge controller)
        self.BatteryDischargeEff = 0.85 #Discharging Efficeicny (Must take into account efficiecny of AC/DC and charge controller)
        self.BatteryRTEff = 0.8 #Round Trip Efficeincy
        self.BatteryNominalCapacity = 150 #AmpHours of Battery Bank
        self.BatteryCurrentCapacity = 150 #AmpHours Assume Battery Bank is fully charge at beginging of simulation
        self.BatteryVoltageNominal = 48    #Volts Nominal Voltage of battery
        self.BatteryVoltageCharge = 50  # Volts Average voltage when charging the battery
        self.BatteryVoltageDischarge = 48 #Volts Average voltage when discharging the battery
        self.BatteryMinCapacityAsFraction = 0.2 #Minimume State of Charge Allowed in Battery
        self.BatteryMaxCRate = 5 #C Maximume charge or discharge rate

        #Load
        self.LoadUncontrollablePower = [] #kW Power requested by loads that are uncontrollable
        self.LoadControllablePower = []  #kW Power requested by loads that are controllable
        self.LoadCurtailPercent = 0    #Percent of load to be curtailed and met at a later time step


class HEMSDataOutput():
    def __init__(self, *args, **kwargs):

        #SolarPV
        self.PVPowerOut = 0; #kW

        #Inverter
        self.IPowerOut = 0; #kW

        #Grid
        self.GridPowerNet = 0; #Net energy comsumed or produced by building (- produce + consume)
        self.GridPower = 0; #kW Power used from grid
        self.GridEnergy = 0; #kWh Energy used from grid

        #Battery
        self.BatteryCurrentCapacity = 0;
        self.BatterySOC = 0; #Present SOC of battery
        self.BatteryPower = 0;  #kW (Power used to charge or discharged from battery)
        self.BatteryPowerAllowable = 0; #Allowable power to be used for charging

        #Load
        self.LoadControllablePowerActual = 0;  # kW Power used by loads that are controllable
        self.LoadPercentCurtail = 0  # Percent of controllable load that is curtailed
