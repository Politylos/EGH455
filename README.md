# EGH455
## EGH455 Advance System Design
This github repository is for group12's EGH455 raspberry pi codebase.

### Raspberry PI login details
The username for the RPi is `group12`.  
The password for `group12` user is `1234`.  

---

## Setup commands
1. Install the Pimoroni Enviro+ Python libraries
```
git clone https://github.com/pimoroni/enviroplus-python
cd enviroplus-python
sudo ./install.sh
```
2. Install the group12 EGH455 libraries
```
git clone https://github.com/kossu-dog/EGH455.git
cd EGH455
sudo ./install.sh
```

---

### Startup script  

Startup script is controlled by systemd. Info can be found at [Five Ways To Run a Program On Your Raspberry Pi At Startup](https://www.dexterindustries.com/howto/run-a-program-on-your-raspberry-pi-at-startup/#systemd).  
To modify the startup script, use the following commands.  
```
sudo nano /lib/systemd/system/startup.service
```
Add the contents of the example `startup.service` file in the `example_files` directory of this repo. Then run the following commands.
```
sudo chmod 644 /lib/systemd/system/startup.service
sudo systemctl daemon-reload
sudo systemctl enable startup.service
sudo reboot
```
Be sure to use absolute path references for all filenames. Use `&` after filename to run as a service.  

---

### User groups
To enable access to the RPi's SPI and I2C drivers without root privilege, the user account must be added to the `dialout` group.  
```
sudo usermod -a -G dialout group12
```

---

### Envrio+ Examples
Example python scripts for the Envrion+ board can be found at the [Envrio+ GITHUB page](https://github.com/pimoroni/enviroplus-python).  
The pinout for the Envrio+ can be found [here](https://pinout.xyz/pinout/enviro_plus).  

---
### GIT Commands

#### Clone repo
```
git clone https://github.com/kossu-dog/EGH455.git
```

#### Commit and push changes to main
```
git add .
git commit -m "Commit comment here"
git push origin main
```

#### Commit and push changes to branch
```
git add .
git commit -m "Commit comment here"
git push origin branch_name
```

#### Pull changes from remote
```
git pull
```

#### Create branch
```
git checkout -b branch_name
```

#### Change branch
```
git checkout branch_name
```

#### Merge branch
```
git checkout main
git merge branch_name
```

#### Delete branch
```
git branch -d branch_name
```

---
