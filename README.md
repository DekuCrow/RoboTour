
<p align="center"><img src="/IMAGES/Logo.png" title="RoboTour" width="245" height="170" align="center" /></p>


<h1  align="center" style="text-align: center;"><span  align="center" style="color: #ff0000;"><strong><span align="center" style="color: #000000;"> SDP - GROUP 18 - 2017/2018</span> </strong></span></h1>
<p style="text-align: center;">&nbsp;</p>


RoboTour is a robotic tour guide that assists people in environments such as museums or art galleries. The system comprises an autonomous robotic guide, a purpose-built Android application, and a web server mediating the communication between the two. RoboTour can be controlled by up to two Android devices. The app allows users to interact with RoboTour intuitively in multiple languages. RoboTour has been designed for minimal maintenance, once the initial setup has been performed. 

[Introduction Video](https://www.youtube.com/watch?v=iU0O0e72A&feature=youtu.be)

[![IMAGE ALT TEXT](http://img.youtube.com/vi/is1U0O0e72A/0.jpg)](http://www.youtube.com/watch?v=is1U0O0e72A&feature=youtu.be "Video Title")

(Directed by Finn, Actors: Alice, Mahbub and Michal)

### [SDP - 2017/2018 ](http://www.drps.ed.ac.uk/17-18/dpt/cxinfr09032.htm)
The System Design Project is intended to give students practical experience of 

(a) building a large scale system 
<br>
<br>
(b) working as members of a team. 

The project involves applying and combining material from several courses to complete a complex design and implementation task. 
At the end, of course, each group demonstrates its implemented system and gives a formal presentation to an audience of the students, supervisors, and visitors from industry.
(http://www.drps.ed.ac.uk/17-18/dpt/cxinfr09032.htm)


### Award - Technical Innovation 
The project was developed for System Design Project at University of Edinburgh.
All 20 projects were assessed by external judges from industry (e.g. Google, Amazon, Accenture, KAL, Sky).
Team RoboTour was awarded  [Technical Innovation Prize](https://www.ed.ac.uk/informatics/news-events/stories/2018/students-showcase-projects-to-industry-experts)
(https://www.ed.ac.uk/informatics/news-events/stories/2018/students-showcase-projects-to-industry-experts)


### Specification
RoboTour provides four key features to enhance the user’s experience

* **Multi-language support in Human-Robot Interaction via speech and app** 
* **Guides visitors to a specific art piece and points it out to the user**
* **Plays audio description of art pieces in the language the user selected** 
* **Provides recommendations and optimal route planning routes**

### Target Users
RoboTour assists people who have one of the following problems:
•    They’re a museum visitor who needs directional assistance
•    Or they’re a visitor who cannot read the displays in the museum whether this is because they cannot read the language or because they have problems with their vision.
Our robot can interact with visitors and guide them to the piece of art they are looking for by moving with the user through the museum and pointing out the art piece upon arrival.

### Software Structure
There are three main components to RoboTour: 
* Android App - Responsible for allowing the user to select paintings they wish to go to and send commands to the robot.
* Server: All Android devices communicate to the robot via the server. The server is responsible for mediating and storing commands between all Android devices and the robot. The purpose of having the server is to allow multiple android devices to communicate with the robot. 
* Robot: Oversees path planning and navigation around the museum
<img src="/IMAGES/table.png" title="RoboTour" width="600" height="120" />

### The App
The app is backwards compatible with older versions of Android; the app will work with Android SDK version 17 onwards (users also require 20mb free space and an internet connection). The app was developed in Android Studio 3.1 using Kotlin. 

### Screenshots

<img src="/IMAGES/s1.png" title="RoboTour" width="200" height="390" /> <img src="/IMAGES/s2.png" title="RoboTour" width="200" height="390" /> <img src="/IMAGES/s3.png" title="RoboTour" width="200" height="390" />   <img src="/IMAGES/s4.png" title="RoboTour" width="200" height="390" />
<br>
<br>
<br>

<img src="/IMAGES/s5.png" title="RoboTour" width="200" height="390" /><img src="/IMAGES/s6.png" title="RoboTour" width="200" height="390" /><img src="/IMAGES/s7.png" title="RoboTour" width="200" height="390" /><img src="/IMAGES/s8.png" title="RoboTour" width="200" height="390" />

### The Robot
The robot is a differential drive platform, i.e. the movement is achieved with two motorised drive wheels. Varying the rotational speed of the wheels independently, allowed us to introduce rotation of the chassis in addition to the linear translation. Additionally, two rear wheels are added for stability and weight support. They were designed with the aim of minimising the friction and disturbance to the robot control.



 <img src="/IMAGES/DSC_0943.JPG" title="RoboTour" width="300" height="190" />
 <img src="/IMAGES/Brochure3Rounded.png" title="RoboTour" width="300" height="190" />
 <img src="/IMAGES/robot.png" title="RoboTour" width="300" height="190" />

<br>

### 


### Installing The App
To install the app on an Android device, installation from unknown sources must be enabled. This feature is turned off by default on stock Android, and can be turned on by following these steps: 

Device Settings ​-> ​Advanced Settings ​-> ​Security ​->​ Enable Unknown Sources   
To download the app visit the following link from your phone: 
https://www.mahbubiftekhar.com/download.php  

A file called RoboTour.apk will begin downloading automatically.   
Once the app is downloaded, go to the Downloads folder on your phone and click on the apk or select it from the notifications bar. Follow the installation instructions. Once installed the app will be in your App drawer under RoboTour. Tap the app to open it. 


## Group Members

* **[Mahbub Iftekhar](https://www.mahbubiftekhar.co.uk/)** - *Team Manager / Android Developer*
* **[David Spears](https://github.com/davidspeers)** - *Android Developer/UI Designer* 
* **[Michal Dauernhauer](https://github.com/michuszkud)** - *Embedded Developer & Custom Sensor Guru*
* **[Alice Wu](https://github.com/AliceWoooo)** -  *Robotics Software Developer*
* **[Devidas Lavrik](https://github.com/DLavrik)** - *Lego Builder & PID Expert* 
* **[Finn Zhan Chen](http://finnzhanchen.com/)** - *Business Analyst*
* **[Mariyana Cholakova](https://github.com/chMariyana)** - *Designer/Admin* 

## Contact us
You are welcome to visit out [Facebook page](https://www.facebook.com/RoboTour/) or send us an e-mail on robotour.sdp@gmail.com 



## Reference

* GitHub. (2018). Kotlin/anko. [online] Available at: https://github.com/Kotlin/anko [Accessed 9 Apr. 2018].

* The Verge. (2018). 99.6 percent of new smartphones run Android or iOS. [online] Available at: https://www.theverge.com/2017/2/16/14634656/android-ios-market-share-blackberry-2016 [Accessed 9 Apr. 2018].

* Google Cloud Speech API. (2018). Cloud Speech API Documentation  |  Google Cloud Speech API  |  Google Cloud. [online] Available at: https://cloud.google.com/speech/docs/ [Accessed 9 Apr. 2018].

* Cloud Text-to-Speech API. (2018). Cloud Text-to-Speech API Basics  |  Cloud Text-to-Speech API  |  Google Cloud. [online] Available at: https://cloud.google.com/text-to-speech/docs/basics [Accessed 9 Apr. 2018].

* Skiena, S. (1990). Dijkstra’s algorithm. Implementing Discrete Mathematics: Combinatorics and Graph Theory with Mathematica, Reading, MA: Addison-Wesley, 225-227.

* Gilles-bertrand.com. (2018). Dijkstra algorithm: How to implement it with Python (solved with all explanations) ? | Gilles' Blog. [online] Available at: http://www.gilles-bertrand.com/2014/03/dijkstra-algorithm-python-example-source-code-shortest-path.html [Accessed 11 Apr. 2018].



