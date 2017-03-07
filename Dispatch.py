#Dispatch Logic

from HEMS_data import HEMSData
data = HEMSData()
import math
import Load
import Inverter
import SolarPV
import Battery

def Dispatch(type, controllableLoadPower, curtail, uncontrollableLoadPower, dayOfYear, localTime, timeZone, longitude, latitude, slope, globalHorizontalRadiation, clearnessIndex, DNI,
            timeStepHourlyFraction, DFI, groundReflectance, inverterEff, pvCapacity, invertCapacity, startTOU, stopTOU, currentCapacity, nominalCapacity, minCapacityAsFractoin, chargeEff, dischargeEff, maxCRate, nominalVoltage):
    #run system simulation

    #TODO: needs lots of conditional logic here to handle various use cases
    powerOutputDC = 0
    powerOutputAC = 0
    batteryPower = 0
    PVPower = 0
    EnergyNet = 0
    batteryCurrentCapacity = currentCapacity
    batterySOC = 0
    capacityAsAmpHour = 0
    if type == 'loads':    #no generators or additional loads(vehicle)...battery only charges from solarPV
        totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
        EnergyNet = totalLoadPower
        powerOutputDC = 0
        powerOutputAC = 0
        batteryPower = 0
        PVPower = 0
        batteryCurrentCapacity = 0
        batterySOC = 0
        capacityAsAmpHour = 0
    elif type == 'solarPV & & inverter':  #solar generator
        powerOutputDC = SolarPV.SolarPV(dayOfYear, localTime, timeZone, longitude, latitude, slope, globalHorizontalRadiation, clearnessIndex, DNI,
            timeStepHourlyFraction, DFI, groundReflectance, pvCapacity)
        powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
        totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
        EnergyNet = totalLoadPower - powerOutputAC
        batteryPower = 0
        PVPower = powerOutputDC
        batteryCurrentCapacity = 0
        batterySOC = 0
        capacityAsAmpHour = 0
    elif type == 'solarPV & & inverter && battery':   #solar and battery
        hourOfDay = localTime
        powerOutputDC = SolarPV.SolarPV(dayOfYear, localTime, timeZone, longitude, latitude, slope,
                                        globalHorizontalRadiation, clearnessIndex, DNI,
                                        timeStepHourlyFraction, DFI, groundReflectance, pvCapacity)
        powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
        totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
        #here is the dispatch logic...
        # - no solar, use grid to meet load
        # - charge battery with solar
        # - send excess to meet load
        # - discharge battery during TOU period battery to avoid high grid price...assume 12-8PM

        if ( hourOfDay < startTOU or hourOfDay > stopTOU ): #outside TOU, don't use battery
            batteryPower, maxChargeEnergy = Battery.BatteryGetMaximumChargePower(currentCapacity, timeStepHourlyFraction,
                                                                                 nominalCapacity, nominalVoltage, minCapacityAsFractoin,
                                                                                 chargeEff, dischargeEff, maxCRate)

            if ( batteryPower > 0 ): #battery has room to be charged
                powerOutputDC = SolarPV.SolarPV(dayOfYear, localTime, timeZone, longitude, latitude, slope, globalHorizontalRadiation,
                            clearnessIndex, DNI, timeStepHourlyFraction, DFI, groundReflectance, pvCapacity)
                powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
                batteryPower, maxChargeEnergy = Battery.BatteryGetMaximumChargePower(currentCapacity, timeStepHourlyFraction,
                                                                                     nominalCapacity, nominalVoltage, minCapacityAsFractoin,
                                                                                     chargeEff, dischargeEff, maxCRate)
                PVPower = powerOutputDC
                if powerOutputDC <= 0: #no solar just use grid to meet load
                    batteryPower = 0
                    powerOutputDC = 0
                    powerOutputAC = 0
                    PVPower = 0
                    totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
                    EnergyNet = totalLoadPower
                elif ( PVPower > batteryPower): #more solar than can put into battery
                    batteryPower = ( -1.0 * batteryPower )  #switch sign so we know it is charging
                    powerOutputDC = powerOutputDC - batteryPower    #send remaining to load
                    powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
                    totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
                    EnergyNet = totalLoadPower - powerOutputAC
                else: #battery requires all solar power, no solar pushed to loads
                    batteryPower = ( -1.0 * powerOutputDC )
                    powerOutputDC = 0  # send remaining to load
                    powerOutputAC = 0
                    totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
                    EnergyNet = totalLoadPower
            else: #no room to charge battery, just push solar to AC
                batteryPower = 0 #still need to do, else numbers don't update
                powerOutputDC = SolarPV.SolarPV(dayOfYear, localTime, timeZone, longitude, latitude, slope,
                                        globalHorizontalRadiation,
                                        clearnessIndex, DNI, timeStepHourlyFraction, DFI, groundReflectance, pvCapacity)
                PVPower = powerOutputDC
                powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
                totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
                EnergyNet = totalLoadPower - powerOutputAC

        else: #inside TOU, use battery if possible
            powerOutputDC = SolarPV.SolarPV(dayOfYear, localTime, timeZone, longitude, latitude, slope,
                                    globalHorizontalRadiation,
                                    clearnessIndex, DNI, timeStepHourlyFraction, DFI, groundReflectance, pvCapacity)
            PVPower = powerOutputDC
            powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
            totalLoadPower = Load.Load(controllableLoadPower, curtail, uncontrollableLoadPower)
            EnergyNet = totalLoadPower - powerOutputAC  # send remaining to grid
            batteryPower, maxChargeEnergy = Battery.BatteryGetMaximumChargePower(currentCapacity, timeStepHourlyFraction,
                                                                                 nominalCapacity, nominalVoltage, minCapacityAsFractoin,
                                                                                 chargeEff, dischargeEff, maxCRate)
            if ( EnergyNet < 0 ):  #use excess power to charge battery
                excessDC = -1*(EnergyNet/inverterEff) #change back to DC and sign from negative to positive
                if batteryPower > 0:
                    if excessDC > batteryPower:  #more solar than can put into battery
                        batteryPower = ( -1.0 * batteryPower ) #switch sign so we know it is charging
                        powerOutputDC = excessDC - batteryPower #send remaining to grid
                        powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)
                        EnergyNet = -1*(powerOutputAC) #send remaining to grid

                    else: #battery requires all solar power, no excess solar pushed to grid
                        batteryPower = (-1.0 * excessDC)  # switch sign so we know it is charging
                        powerOutputDC = excessDC
                        powerOutputAC = 0
                        EnergyNet = 0
                else: #no room to charge battery, just push solar to AC
                    batteryPower = 0 #still need to do, else numbers don't update
                    powerOutputDC = excessDC
                    powerOutputAC = Inverter.Inverter(excessDC, inverterEff, pvCapacity, invertCapacity)
                    EnergyNet = -1*(powerOutputAC)  # send remaining to grid
            else: #try use battery to meet load
                deficitAC = totalLoadPower - powerOutputAC  #how much AC load battery has to supply
                deficitDC = deficitAC/inverterEff   #account for DC to AC efficiency
                batteryPower, maxDischargeEnerg = Battery.BatteryGetMaximumDischargePower(currentCapacity, timeStepHourlyFraction,
                                                                                          nominalCapacity, nominalVoltage, minCapacityAsFractoin,
                                                                                          chargeEff, dischargeEff, maxCRate)
                if (batteryPower > 0):
                    if ( deficitDC > batteryPower ): #need more power than battery can deliver
                        batteryPower = (batteryPower) #positive sign means discharging
                        powerOutputDC = powerOutputDC + batteryPower #account for extra battery power going into inverter
                        powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity) #solar output + battery output
                        EnergyNet = totalLoadPower - powerOutputAC

                    else:   #battery can meet deficit DC that solar PV cannot
                        batteryPower = (deficitDC)
                        powerOutputDC = powerOutputDC + batteryPower  # account for extra battery power going into inverter
                        powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)  # solar output + battery output
                        EnergyNet = totalLoadPower - powerOutputAC


                else:   #no energy in battery to use
                    batteryPower = 0  # still need to do, else numbers don't update
                    powerOutputDC = powerOutputDC + batteryPower  # account for extra battery power going into inverter
                    powerOutputAC = Inverter.Inverter(powerOutputDC, inverterEff, pvCapacity, invertCapacity)  # solar output + battery output
                    EnergyNet = totalLoadPower - powerOutputAC

    batteryCurrentCapacity, batterySOC, capacityAsAmpHour = Battery.BatteryCapacity(batteryPower, currentCapacity, nominalVoltage, nominalCapacity, chargeEff, dischargeEff)


    return powerOutputDC,powerOutputAC,batteryPower,EnergyNet, batteryCurrentCapacity, batterySOC, capacityAsAmpHour, PVPower