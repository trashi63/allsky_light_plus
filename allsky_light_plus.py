'''
AllSky Light Plus – Enhanced AllSky Light Meter
Author: Helmut Hoerschgl
Based on original work by Alex Greenland (AllSky Team)
'''

import allsky_shared as s
import sys, math, board, busio, adafruit_tsl2591, adafruit_tsl2561, datetime, csv, os, time, json

metaData = {
    "name": "AllSky Light Plus",
    "description": "Enhanced AllSky Light Meter with SQM, Bortle color, and calibration logging.",
    "module": "allsky_light_plus",
    "version": "v1.2.1",
    "author": "Helmut Hoerschgl (based on work by Alex Greenland, AllSky Team)",
    "authorurl": "https://github.com/trashi63/allsky_light_plus",
    "events": ["periodic"],
    "experimental": "false",
    "arguments": {
        "type": "TSL2591",
        "i2caddress": "",
        "tsl2591gain": "25x",
        "tsl2591integration": "100ms",
        "tsl2561gain": "Low",
        "tsl2561integration": "101ms",
        "extradatafilename": "allskylight.json"
    },
    "argumentdetails": {
        "type": {
            "required": "true",
            "description": "Sensor Type",
            "help": "Select which TSL sensor is used.",
            "type": {"fieldtype": "select", "values": "None,TSL2591,TSL2561", "default": "TSL2591"}
        },
        "i2caddress": {
            "required": "false",
            "description": "I2C Address",
            "help": "Optional override for sensor I2C address (hex, e.g. 0x29)."
        },
        "tsl2591gain": {
            "required": "false",
            "description": "TSL2591 Gain",
            "help": "Gain setting for the TSL2591.",
            "tab": "TSL2591",
            "type": {"fieldtype": "select", "values": "1x,25x,428x,9876x", "default": "25x"}
        },
        "tsl2591integration": {
            "required": "false",
            "description": "TSL2591 Integration time",
            "help": "Integration time for the TSL2591 sensor.",
            "tab": "TSL2591",
            "type": {"fieldtype": "select", "values": "100ms,200ms,300ms,400ms,500ms,600ms", "default": "100ms"}
        },
        "tsl2561gain": {
            "required": "false",
            "description": "TSL2561 Gain",
            "help": "Gain setting for the TSL2561.",
            "tab": "TSL2561",
            "type": {"fieldtype": "select", "values": "Low,High", "default": "Low"}
        },
        "tsl2561integration": {
            "required": "false",
            "description": "TSL2561 Integration time",
            "help": "Integration time for the TSL2561 sensor.",
            "tab": "TSL2561",
            "type": {"fieldtype": "select", "values": "13.7ms,101ms,402ms", "default": "101ms"}
        },
        "extradatafilename": {
            "required": "true",
            "description": "Extra Data Filename",
            "tab": "Advanced",
            "help": "JSON file used for overlay data output."
        }
    },
    "businfo": ["i2c"],
    "enabled": "false",
    "changelog": {
        "v1.2.1": [ {
            "author": "Helmut Hoerschgl",
            "changes": [
                "Added calibration logging (CSV).",
                "Added Bortle color output.",
                "Improved metadata for AllSky Module Manager."
            ]
        } ]
    }
}

CALIBRATION_OFFSET = 0.0

def sanitize_text(t):
    return (t.replace("\\u2013","-").replace("–","-")
             .replace("ä","ae").replace("ö","oe").replace("ü","ue")
             .replace("Ä","Ae").replace("Ö","Oe").replace("Ü","Ue"))

def readTSL2591(p):
    i2c = board.I2C()
    try:
        s_addr = int(p['i2caddress'],16) if p['i2caddress'] else None
        sensor = adafruit_tsl2591.TSL2591(i2c, s_addr) if s_addr else adafruit_tsl2591.TSL2591(i2c)
        g = p["tsl2591gain"]
        sensor.gain = {"1x":adafruit_tsl2591.GAIN_LOW,"25x":adafruit_tsl2591.GAIN_MED,
                       "428x":adafruit_tsl2591.GAIN_HIGH,"9876x":adafruit_tsl2591.GAIN_MAX}.get(g, adafruit_tsl2591.GAIN_MED)
        i = p["tsl2591integration"].replace("ms","MS")
        sensor.integration_time = getattr(adafruit_tsl2591,f"INTEGRATIONTIME_{i}")
        return sensor.lux, sensor.infrared, sensor.visible
    except Exception as e:
        s.log(0,f"ERROR TSL2591: {e}")
        return None,None,None

def readTSL2561(p):
    i2c = busio.I2C(board.SCL, board.SDA)
    try:
        s_addr = int(p['i2caddress'],16) if p['i2caddress'] else None
        tsl = adafruit_tsl2561.TSL2561(i2c,s_addr) if s_addr else adafruit_tsl2561.TSL2561(i2c)
        tsl.gain = 0 if p["tsl2561gain"]=="Low" else 1
        tsl.integration_time = {"13.7ms":0,"101ms":1,"402ms":2}.get(p["tsl2561integration"],1)
        lux = tsl.lux or 0
        return lux, tsl.infrared, tsl.broadband
    except Exception as e:
        s.log(0,f"ERROR TSL2561: {e}")
        return None,None,None

def light_plus(p,event):
    sensor = p["type"].lower()
    f = p["extradatafilename"]
    if sensor == "none":
        s.deleteExtraData(f); s.log(0,"ERROR: No sensor defined"); return "No sensor defined"
    lux,_,_ = (readTSL2591(p) if sensor=="tsl2591" else readTSL2561(p) if sensor=="tsl2561" else (None,None,None))
    if lux is None: s.deleteExtraData(f); s.log(0,f"ERROR reading {sensor}"); return f"Error reading {sensor}"
    if lux<=0: lux=0.0001
    sqm=(math.log10(lux/108000)/-0.45)+CALIBRATION_OFFSET
    nelm=7.93-5.0*math.log10((pow(10,(4.316-(sqm/5.0)))+1.0))
    if sqm<18.0: rating,color="Sehr hell (Bortle 8-9, Stadtzentrum)","#FF0000"
    elif sqm<19.5: rating,color="Hell (Bortle 7-8, Stadtrand)","#FF8000"
    elif sqm<20.5: rating,color="Maessig (Bortle 5-6, Vorort)","#FFFF00"
    elif sqm<21.3: rating,color="Gut (Bortle 4-5, laendlich)","#80FF00"
    elif sqm<21.8: rating,color="Dunkel (Bortle 3-4, laendlich)","#00FF00"
    else: rating,color="Exzellent (Bortle 1-2, sehr dunkler Himmel)","#00FFFF"
    rating=sanitize_text(rating)
    data={"AS_LIGHTLUX":f"{lux:.2f}","AS_LIGHTNELM":f"{nelm:.2f}",
          "AS_LIGHTSQM":f"{sqm:.2f}","AS_LIGHTDESC":rating,"AS_LIGHTCOLOR":color}
    s.saveExtraData(f,data); s.log(4,f"INFO: Lux {lux:.2f}, SQM {sqm:.2f} — {rating}")
    return f"Lux {lux:.2f}, NELM {nelm:.2f}, SQM {sqm:.2f} — {rating}"

def calibration_mode(p,samples=20,delay=60):
    path="/home/pi/allsky/config/overlay/extra/sqm_calibration_log.csv"
    if not os.path.exists(path):
        with open(path,"w",newline="") as f: csv.writer(f).writerow(["Timestamp","Lux","SQM_raw","SQM_adj","NELM","Rating","Offset"])
    for i in range(samples):
        light_plus(p,"calibration")
        try:
            with open("/home/pi/allsky/config/overlay/extra/allskylight.json") as jf: d=json.load(jf)
            lux=float(d.get("AS_LIGHTLUX",0)); sqm=float(d.get("AS_LIGHTSQM",0)); nelm=float(d.get("AS_LIGHTNELM",0))
            rating=d.get("AS_LIGHTDESC",""); sqm_adj=sqm+CALIBRATION_OFFSET
            with open(path,"a",newline="") as f:
                csv.writer(f).writerow([datetime.datetime.now().isoformat(sep=" ",timespec="seconds"),
                lux,f"{sqm:.3f}",f"{sqm_adj:.3f}",f"{nelm:.3f}",rating,CALIBRATION_OFFSET])
            s.log(4,f"Calibration {i+1}/{samples}: SQM {sqm_adj:.2f} ({rating})")
        except Exception as e: s.log(0,f"Calibration log error: {e}")
        time.sleep(delay)
    s.log(3,f"Calibration complete — data saved to {path}")

def light_cleanup():
    s.cleanupModule({"metaData":metaData,"cleanup":{"files":{"allskylight.json"},"env":{}}})

if __name__=="__main__": light_plus(metaData["arguments"],"periodic")
