# 2022-LSSE-Brain-based-Wheelchair-Control

Software Systems Engineering project.

## Overview

This project was made by 6 people for an University of Pisa exam. The project consists of simplified software with the purpose of developing a classifier for recognizing mantal commands (move, stop, left, right) in order to control a wheelchair.

Inside the documentation in 'doc' folder it's possible to see the Landscape, BPMNs, Use Cases, Sequence Diagrams, Analysis Class Diagrams, Design Class diagrams, Non-Responsiveness test, Non-Elasticiy test, Non-Interoperability test, Non-Resiliency test, Non-Automation test.

## Objective
Drive the wheelchair via EEG headset.

## Specifications
The wheelchair can be guided using only EEGs, with a difference for indoor and outdoor environments, as the
latter is richer in stimuli and require faster reactions. The command imagined for the wheelchair can be "turn
2/5 right", "turn left" and "move". 

Every 3-4 seconds the following data sources are provided by independent systems:
1) headset => UUID, EEG-data; 
2) calendar => UUID, activity (sport, shopping, home, working); 
3) command thought => UUID, command (left, right, move; stop) 
4) environment => UUID, environment (indoor, outdoor). 

On the basis of (1) (2) (4) the classifier will determine (3).

## Authors

* Biagio Cornacchia, b.cornacchia@studenti.unipi.it
* Francesco Martoccia, f.martoccia@studenti.unipi.it
* Gianluca Gemini, g.gemini@studenti.unipi.it
* Luca Tartaglia, l.tartaglia@studenti.unipi.it
* Matteo Abaterusso, m.abaterusso@studenti.unipi.it
* Salvatore Lombardi, s.lombardi38@studenti.unipi.it