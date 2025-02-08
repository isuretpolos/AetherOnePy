# AetherOnePy Server written in Python
This is the open source implementation of the AetherOnePy. It runs on many different hardware configurations, like Windows, Linux, Mac and Raspberry Pi.

# Get hotbits
1) Check if the server is installed inside a RaspberryPi and then get the dev/random stream
2) If not, check if you have a webcam available and get it from the noise of the camera (cheaper are better)
3) If not, check if an Arduino is connected via serial usb and let it deliver to you
4) If not switch mode to "simulation" and let the operator know

# Database
## Cases, Sessions, Analysis and Rates
```sql
select * from
	cases c
	join sessions s on c.id = s.case_id
	left join analysis a on s.id = a.session_id
	left join rate_analysis ra on a.id = ra.analysis_id 
```