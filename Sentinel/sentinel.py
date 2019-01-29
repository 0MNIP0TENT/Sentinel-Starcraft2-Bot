import sc2
from sc2 import run_game, maps, Race, Difficulty, position
from sc2.position import Point2
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ROBOTICSFACILITY, ASSIMILATOR, GATEWAY, \
 CYBERNETICSCORE, STALKER, IMMORTAL,STARGATE, VOIDRAY, ZEALOT, FORGE, PHOTONCANNON, \
 STARGATE, FLEETBEACON, VOIDRAY, CARRIER, SENTRY, PROTOSSAIRWEAPONSLEVEL1, \
 PROTOSSAIRARMORSLEVEL1
import random
from random import randint
from operator import or_
from sc2.constants import *

class Sentinel(sc2.BotAI):

    def __init__(self):
        self.air_weapon1_started = False 
        self.air_weapon2_started = False
        self.air_weapon3_started = False

        self.air_armor1_started = False
        self.air_armor2_started = False
        self.air_armor3_started = False
        
    async def on_step(self,iteration):
        await self.distribute_workers()

        await self.expand()

        await self.build_workers()

        await self.build_buildings()

        await self.build_army()

        await self.upgrade_air()

        await self.patrol(iteration)

        await self.attack()

        await self.scout()

    async def scout(self):
        if self.supply_used >= 190:
            if not self.units(ZEALOT).ready.exists:
                for gateway in self.units(GATEWAY).ready.noqueue:
                    if self.can_afford(ZEALOT):
                        await self.do(gateway.train(ZEALOT))
            if self.units(ZEALOT).ready.exists:
                scout = self.units(ZEALOT).first
                if scout.is_idle:
                    await self.do(scout.attack(random.choice(self.enemy_start_locations)))
          

    async def expand(self):
        if self.units(NEXUS).amount < 2 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()
        if self.supply_used > 80 and self.units(NEXUS).amount < 3 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()
        if self.supply_used > 120 and self.units(NEXUS).amount < 4 and self.can_afford(NEXUS) and not self.already_pending(NEXUS):
            await self.expand_now()        

    async def build_workers(self):
        if (len(self.units(NEXUS)) * 16) > len(self.units(PROBE)):
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.can_afford(PROBE) and not self.already_pending(PROBE):
                    await self.do(nexus.train(PROBE))

    # build build buildings code

    async def build_buildings(self):

        # build pylons

        await self.build_pylons()

        # build assimilators

        await self.build_assimilators()

        # build gateways

        await self.build_gateways()

        # build cybernetics core

        await self.build_ccore()
        
        # build photon cannons
        #await self.build_cannons()
                
        # build stargate
        await self.build_stargates()

        # build fleet beacon
        await self.build_fleet_beacon()
       
        #build robotics facility
        #await self.build_robotics_facility()

    # build pylons
    async def build_pylons(self):
        if self.supply_left < 10 and not self.supply_cap == 200:
            nexuses = self.units(NEXUS).ready
            if nexuses.exists:
                if self.can_afford(PYLON):
                    # if self.units(PYLON).amount < 1:
                    #     await self.build(PYLON, self.main_base_ramp.top_center)
                    # else:    
                        await self.build(PYLON, near=nexuses.first)
                     
    #  -> builds assimilators                
    async def build_assimilators(self):
        for nexus in self.units(NEXUS).ready:
            vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
            for vaspene in vaspenes:
                if not self.can_afford(ASSIMILATOR) and not self.already_pending(ASSIMILATOR):
                    break
                worker = self.select_build_worker(vaspene.position)
                if worker is None:
                    break
                if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                    await self.do(worker.build(ASSIMILATOR, vaspene))    
 
     #  -> builds gateway(s)
    async def build_gateways(self):
        if self.units(GATEWAY).amount < 1:
            if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                if self.units(PYLON).ready.exists:
                    pylon = self.units(PYLON).random
                    await self.build(GATEWAY, near=pylon)

    #  -> builds cynernetics core
    async def build_ccore(self):
        if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
            if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
                pylon = self.units(PYLON).random
                await self.build(CYBERNETICSCORE, near=pylon)
        
    # -> builds stargates
    async def build_stargates(self):
        if self.units(CYBERNETICSCORE).ready.exists:   
            if self.can_afford(STARGATE) and self.units(STARGATE).amount < 2:
                pylon = self.units(PYLON).random
                await self.build(STARGATE, near=pylon)
            elif self.units(VOIDRAY).amount + self.units(CARRIER).amount > 3 and self.units(STARGATE).amount < 3:
                pylon = self.units(PYLON).ready.random
                await self.build(STARGATE, near=pylon)
            elif self.supply_used > 195 and self.units(STARGATE).amount < 7:
                pylon = self.units(PYLON).random
                await self.build(STARGATE, near=pylon)
    

    async def build_fleet_beacon(self):
        if not self.units(FLEETBEACON).ready.exists and not self.already_pending(FLEETBEACON):
            if self.units(PYLON).ready.exists:
                pylon = self.units(PYLON).ready.random
                await self.build(FLEETBEACON, near=pylon)

    #  -> builds forge
    async def build_forge(self):
        if self.units(FORGE).amount < 1 and self.can_afford(FORGE):
            if not self.already_pending(FORGE):
                pylon = self.units(PYLON).random
                await self.build(FORGE, near=pylon)


    # -> build robotics facility
    async def build_robotics_facility(self):
        if self.units(CYBERNETICSCORE).ready.exists:
            if self.units(ROBOTICSFACILITY).amount < 3 and not self.already_pending(ROBOTICSFACILITY):
                if self.can_afford(ROBOTICSFACILITY):
                    pylon = self.units(PYLON).random
                    await self.build(ROBOTICSFACILITY, near=pylon)

    # -> build cannons
    async def build_cannons(self):
        await self.build_forge()
        # build PHOTONCANNONs
        if self.units(PYLON).ready.exists and self.units(PHOTONCANNON).amount < 20:
            pylon = self.units(PYLON).random
            await self.build(PHOTONCANNON, near=pylon)

    # -> End of building code


    # -> training army code

    async def build_army(self):
      
        #train zealots
        await self.train_zealots()
    
        #await self.train_sentrys()   

        #await self.train_stalkers()

        #await self.train_immortals()

        await self.train_voidrays()

        await self.train_carriers() 

    # train zealots    
    async def train_zealots(self):
        if not self.units(FLEETBEACON).ready.exists:   
            for gateway in self.units(GATEWAY).ready.noqueue:
                if self.can_afford(ZEALOT):
                    await self.do(gateway.train(ZEALOT))

    # train sentrys
    async def train_sentrys(self):
        for gateway in self.units(GATEWAY).ready.noqueue:
            if self.can_afford(SENTRY) and self.units(CYBERNETICSCORE).ready.exists:
                if self.units(SENTRY).amount <= self.units(STALKER).amount / 5:
                    await self.do(gateway.train(SENTRY))                
    # train stalkers
    async def train_stalkers(self):
        if not self.units(FLEETBEACON).ready:
            for gateway in self.units(GATEWAY).ready.noqueue:
                if self.can_afford(STALKER):
                    await self.do(gateway.train(STALKER))            

    # train immortal
    async def train_immortals(self):
        if self.units(ROBOTICSFACILITY).ready.exists:
            for robofac in self.units(ROBOTICSFACILITY):
                if self.can_afford(IMMORTAL):
                    await self.do(robofac.train(IMMORTAL))

    # train voidrays
    async def train_voidrays(self):
        for stargates in self.units(STARGATE).ready.noqueue:
            if self.units(FLEETBEACON).ready.exists:
                if self.units(VOIDRAY).amount < self.units(CARRIER).amount * 3: 
                    if self.can_afford(VOIDRAY):
                        await self.do(stargates.train(VOIDRAY))   
            else:
                if self.can_afford(VOIDRAY):
                        await self.do(stargates.train(VOIDRAY))

    async def train_carriers(self):
        if self.units(FLEETBEACON).ready.exists:
            for stargate in self.units(STARGATE).ready.noqueue:
                if self.can_afford(CARRIER):
                   await self.do(stargate.train(CARRIER))
    # End of training 

    def find_target(self, state):
        if len(self.known_enemy_units) > 0:
            return random.choice(self.known_enemy_units)
        elif len(self.known_enemy_structures) > 0:
            return random.choice(self.known_enemy_structures)
        else:
            # for one opponet
            #return self.enemy_start_locations[0]
            # for multiple opponets
            return random.choice(self.enemy_start_locations)

    # patrol function
    async def patrol(self,iteration):
        enemys = self.known_enemy_units
        if self.units(NEXUS).amount > 1 and self.supply_used < 150:
            if iteration % 20 == 0:
                forces = self.units(VOIDRAY).ready.idle | self.units(CARRIER).ready.idle | self.units(ZEALOT).ready.idle
            
                
                orders = []
        
                bases = self.units(NEXUS)
        
                for unit in forces:  
                # create order list
            
                    for base in bases:
                        destination = randint(4,15)
                        pos = base.position.to2.towards(self.game_info.map_center,destination)
                        orders.append(unit.move(pos))
           
                
                await self.do_actions(orders)

        if enemys.exists:
            forces = forces = self.units(VOIDRAY).ready.idle | self.units(CARRIER).ready.idle  
            for unit in forces:
                enemys_in_range = enemys.in_attack_range_of(unit)
                if enemys_in_range.exists:
                    self.do(unit.stop())
                    target = enemys_in_range.random
                    self.do(unit.attack(target))


    # attack function
    async def attack(self):
        #target = self.find_target(self.state)
        
        await self.zealot_attack()
        
        await self.sentry_attack()

        await self.stalker_attack()

        await self.immortal_attack()

        await self.voidray_attack()       
    
        await self.carrier_attack()
        

    async def zealot_attack(self):
        if len(self.known_enemy_units):        
            for zealot in self.units(ZEALOT):
                if zealot.is_idle:
                    await self.do(zealot.attack(random.choice(self.known_enemy_units)))

    async def sentry_attack(self):
        if len(self.known_enemy_units) > 0:
            for sentry in self.units(SENTRY):
                abilites = await self.get_available_abilities(sentry)
                if AbilityId.GUARDIANSHIELD_GUARDIANSHIELD in abilites:
                    await self.do(sentry(AbilityId.GUARDIANSHIELD_GUARDIANSHIELD))
                    await self.do(sentry.attack(random.choice(self.known_enemy_units)))

    async def stalker_attack(self):
        
        # if self.supply_used > 185:
        #     for stalker in self.units(STALKER).idle:
        #         await self.do(s.attack(self.find_target(self.state)))

        if len(self.known_enemy_units) > 0:    
            for stalker in self.units(STALKER):
                await self.do(stalker.attack(random.choice(self.known_enemy_units)))

    async def immortal_attack(self):
        if len(self.known_enemy_units) > 0:    
            for immortal in self.units(IMMORTAL):
                await self.do(immortal.attack(random.choice(self.known_enemy_units)))

    async def voidray_attack(self):
        if len(self.known_enemy_units) > 0 and self.supply_used > 100:
            fighting_units = self.known_enemy_units.not_structure       
            if len(fighting_units) < 2:
                for voidray in self.units(VOIDRAY):
                    if voidray.is_idle:
                        await self.do(voidray.attack(random.choice(self.known_enemy_units)))
            else:
                for voidray in self.units(VOIDRAY):
                    if voidray.is_idle:
                        await self.do(voidray.attack(random.choice(fighting_units)))

        # if len(self.known_enemy_units) < 1:
        #     for voidray in self.units(VOIDRAY):
        #         if voidray.is_idle and self.units(NEXUS). amount > 1:
        #             await self.do(voidray.move(self.units(NEXUS).random))


    async def carrier_attack(self):
        if len(self.known_enemy_units) > 0 and self.supply_used > 100:        
            fighting_units = self.known_enemy_units.not_structure      
            if len(fighting_units) < 2:    
                for carrier in self.units(CARRIER):
                    if carrier.is_idle:
                        await self.do(carrier.attack(random.choice(self.known_enemy_units)))    
            else:
                for carrier in self.units(CARRIER):
                    if carrier.is_idle:
                        await self.do(carrier.attack(random.choice(fighting_units)))
        
        # if len(self.known_enemy_units) < 1:
        #     for carrier in self.units(CARRIER):
        #         if carrier.is_idle and self.units(NEXUS).amount > 1:
        #             await self.do(carrier.move(self.units(NEXUS).random))

    async def upgrade_air(self):
        
        if self.units(CYBERNETICSCORE).ready.exists and self.supply_used > 30:
            if self.can_afford(UpgradeId.PROTOSSAIRWEAPONSLEVEL1) and not self.air_weapon1_started:
                ccore = self.units(CYBERNETICSCORE).ready.first
                await self.do(ccore.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL1))
                self.air_weapon1_started = True

            if self.can_afford(UpgradeId.PROTOSSAIRARMORSLEVEL1) and not self.air_armor1_started:
                ccore = self.units(CYBERNETICSCORE).ready.first
                await self.do(ccore.research(UpgradeId.PROTOSSAIRARMORSLEVEL1))
                self.air_armor1_started = True

            if self.air_armor1_started and self.air_weapon1_started:
                if not self.units(FLEETBEACON).ready.exists and not self.already_pending(FLEETBEACON):
                    pylon = self.units(PYLON).ready.random
                    await self.build(FLEETBEACON, near=pylon)

            if self.units(FLEETBEACON).ready.exists:
                if self.supply_used > 100:   
                    if self.can_afford(UpgradeId.PROTOSSAIRARMORSLEVEL2) and not self.air_armor2_started:    
                        ccore = self.units(CYBERNETICSCORE).ready.first
                        await self.do(ccore.research(UpgradeId.PROTOSSAIRARMORSLEVEL2))
                        self.air_armor2_started = True

                    if self.supply_used > 100:
                        if self.can_afford(UpgradeId.PROTOSSAIRWEAPONSLEVEL2) and not self.air_weapon2_started:    
                            ccore = self.units(CYBERNETICSCORE).ready.first
                            await self.do(ccore.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL2))
                            self.air_armor2_started = True

                        if self.can_afford(UpgradeId.PROTOSSAIRARMORSLEVEL3) and not self.air_armor3_started:    
                            ccore = self.units(CYBERNETICSCORE).ready.first
                            await self.do(ccore.research(UpgradeId.PROTOSSAIRARMORSLEVEL3))
                            self.air_armor2_started = True
            
                        if self.can_afford(UpgradeId.PROTOSSAIRWEAPONSLEVEL3) and not self.air_weapon3_started:    
                            ccore = self.units(CYBERNETICSCORE).ready.first
                            await self.do(ccore.research(UpgradeId.PROTOSSAIRWEAPONSLEVEL3))
                            self.air_armor2_started = True

if __name__ == '__main__':   
    run_game(maps.get("PaladinoTerminalLE"), [
        Bot(Race.Protoss, Sentinel()),
        Computer(Race.Zerg, Difficulty.VeryHard),
        #Computer(Race.Protoss, Difficulty.Harder),
        #Computer(Race.Protoss, Difficulty.Harder),
        #Bot(Race.Protoss, SentdeBot())
        ], realtime=True)