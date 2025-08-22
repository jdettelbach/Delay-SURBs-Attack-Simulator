# Delay-SURBs Attack Simulator

This repository contains a mix network simulator written in Python, that can execute a Delay-SURBs Attack.
The Simulator extends the Simulator of Piotrowska (https://github.com/aniampio/Simulator) to analyse Delay-SURBs Attacks on Nym. The basic functionality of Piotrowskas Simulator is preserved in the "test" mode.

Dependencies can be installed by running

    pip3 install -r requirements.txt

To run the simulator, run main.py with the following optional parameters:

	-mode: The mode to run the simulator in; "test" for Piotrowskas simulation, "attacker" for Delay-SURBs attack
	-exp_dir: define experiment directory(default: measurements)
	-config_file: define the configuration file to use(default: test_config.json)

Added configuration options include:

- phases:attack: time added to simulation in attacker mode to execute Delay-SURBs attack(flood network with SURBs)
- network:delay: true, if network delay between nodes should be simulated
- network:gateway: only applies if network delay is also true; simulates sending from client to gateway to first mix with 2 network delays; only one network delay applied if set to false


## Sample Data
contains data of a simulated Delay-SURBs attack with 50 SURBs

File | Content
---- | ------
sampleData/50SURBs | All simulations with 50 SURBs are found here
sampleData/50SURBs/1/short_packet_log.csv | Due to space constraints shortened packet log of a Delay-SURBs attack with 50SURBs (output of the simulator)
sampleData/50SURBs/1/user_arrival_rates_in_100ms.csv | arrival rates per user and 100ms derived from the packet log
sampleData/50SURBs/1/even_gateway_arrival_rates_in_100ms.csv | arrival rates of 166 gateways, each serving 6 users. Derived frompacket log 	
sampleData/50SURBs/1/comparison_rates_in_100ms.csv | comparison of average of all uninvolved clients to the victim of the Delay-SURBs attack
sampleData/50SURBs/arrival_rates_in_100ms.csv | arrival rates of clients averaged over 100 Delay-SURBs attacks with 50 SURBs; compares uninvolved clients to victim and arriving SURBs
sampleData/50SURBs/total_even_gateway_arrival_rates_in_100ms.csv | gateway arrival rates (6 clients serviced each) averaged over 100 Delay-SURBs attacks with 50 SURBs; compares uninvolved gateways to victim's gateway and arriving SURBs
