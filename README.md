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
