This was a project based on FTC, a robotics competition consisting of an autonomous period, and a driver-controlled period. Because the parts to buy the official products would be absurdly costly, I chose to opt for a much cheaper solution, Raspberry Pi. Raspberry Pi's have support for motors, using control boards. This project aims to have a robot that is drivable with WASD through a locally hosted website, or with controller support. The robot would also have the ability to direct itself to a QR code autonomously. 
4/12/24 Final Commit! Today this long project has concluded. The project concluded with a full test of autonomous capabilities which proved to be successful. 

Technical parts and comments:
2 battery packs were used, with a total of around 9 AA batteries used to power 4 TT motors. The Rasberry Pi was powered by a backup power supply, which ironically needed a mobile power supply to stop the motors from whining (my theory is low voltage)

2 L298N motor controllers were controlling omni-directional mecanum wheels. A Logitech C270 camera was used for the camera. Because the camera quality is not the highest, for repeating this project I would recommend either a higher quality camera or printing a QR code that would take up the full 8.5x11 paper size. 

To host the website on 0.0.0.0 on my network, I had to use the command ifconfig, and used the ip address listed under inet, which should be entered on another computer or device. 

One note is the constant need to unplug and plug back in the camera. One reason I could suspect is low voltage, or possibly this isn't the right camera for the job, and it was more forced.

PS: If you want the final code its LiveStreamAndInputs.py, and if you want QR recognizer it will be under QrCodeLocation
