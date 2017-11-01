/*

//////////////////////////
//  AUTHOR INFORMATION  //
//////////////////////////

Copyright 2017 Daniel Meusburger + ETH Zürich

/////////////////////////
// LICENSE INFORMATION //
/////////////////////////

NOTICE: This work product uses the following references. The code of the references WAS CHANGED.

REFERENCES

1. William Malone (www.williammalone.com): CREATE A GAME CHARACTER WITH HTML5 AND JAVASCRIPT http://www.williammalone.com/articles/create-html5-canvas-javascript-game-character/1/
   > Used tutorial as a main reference to go through the steps of creating the avatar. 
   > Original file is licensed based on Apache License 2.0
   > Only parts of the code were re-used, not the full referenced work / files
   > Full download of the contributors work http://www.williammalone.com/articles/create-html5-canvas-javascript-game-character/1/

	 Copyright 2011 William Malone (www.williammalone.com)

	 Licensed under the Apache License, Version 2.0 (the "License");
	 you may not use this file except in compliance with the License.
	 You may obtain a copy of the License at

	  http://www.apache.org/licenses/LICENSE-2.0
	  
	 Unless required by applicable law or agreed to in writing, software
	 distributed under the License is distributed on an "AS IS" BASIS,
	 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
	 See the License for the specific language governing permissions and
	 limitations under the License.

*/

///////////////////////////
//   GENERAL VARIABLES   //
///////////////////////////

// Canvas
var canvas;
var touchzone;
var canvasWidth;
var canvasHeight;
var context;
var ctx;

// Image Loading
var images = {};
var totalResources = 50; 
var numResourcesLoaded = 0;

// FPS
var fps = 30; 
//var fpsInterval = setInterval(updateFPS, 1000);
//var numFramesDrawn = 0;
//var curFPS = 0;

// Global Coordinates
var x;
var y;
var leftOffset; // used to position all elements with space on the left
var w; //w and h are used to scale the images to the viewport (responsive behavior)
var h;

// Error Handling
var testInternetConnection;
var error = 0;

// Canvas Drawing
var redrawCounter = 0;

//////////////////////////////
//   ANIMATION  VARIABLES   //
//////////////////////////////

// Breathing Animation
var breathIncrement = 0.1;
var breathDirection = -1;
var curBreath = 0;
var maxBreath = 1.5;
var breathInterval = setInterval(updateBreath, 1000 / fps);

// Waving Animation
var waveIncrement = 1;
var waveDirection = 1;
var curWaveRot = 0;
var maxWaveRot = 20;
var waveInterval = setInterval(updateWaving, 1000 / fps);

// Blinking Animation
var maxEyeHeight = 6;
var curEyeHeight = maxEyeHeight;
var eyeOpenTime = 0;
var timeBetweenBlinks = 4000;
var blinkUpdateTime = 50;                    
var blinkTimer = setInterval(updateBlink, blinkUpdateTime);
var eyesNotUpdated = 0;

// Healthy Behavior Animation (Arm)
var tarEatRotation = 150;
var curEatRotation = 1;
var baseEatRotation = 1;
var timeBtwEat = 2000;
var eatUpdateTime = 10;         
var didntEatTime = 0;           
var eat = 0;
var eatTimer;
var eatAssetActive = getRandomNumber(0,2);
var eatActive = 1;

var eatAdjustX;
var eatAdjustY;

var eatAssets = ["cherry","carrot","apple","peach","pear"];

// Chew animation
var curMouthHeight;
var chewing = 0;
var chewTime = 0;


/////////////////////////////
//  AVATAR DATA VARIABLES  //
/////////////////////////////

// General user data
var name;
var age;
var gender;
var bodysize;
var bodyweight;
var BMI;

// Get number of views (to check if tutorial should be shown)
var showTutorial;
var tutorialActive = 0;
var tutorialStep = 1;

// Avatar Customization Variables
var trousers_type; // defines lower body outfit
var chest_type; // defines upper body outfit
var head_type; // defines head type
var eyes_type; 
var eyecolor_type;
var nose_type;
var hair_type;
var beard_type;
var glasses_type;
var shoes_type;
var skincolor_type;

// DM: Get the selected design variables from server
var vLeftLeg;
var vRightLeg;
var vLeftUpperArm;
var vRightUpperArm;
var vLeftArm;
var vRightArm;
var vHip;
var vChest; //Shirt
var vHead;
var vEyes;
var vNose;
var vHair;
var vBeard;
var vGlasses;
var vShoes;
var vSkinColor;
var vEyeColor;

// Get the ingredient intake levels 
var db_salt_lvl;
var db_sugar_lvl;
var db_alcohol_lvl;
var db_fv_lvl;
var db_lastday_lvl;

//  Get the last tracked days (old) values for visual variables 
var db_old_undefined;
var db_old_heart_lvl;
var db_old_skin_lvl;
var db_old_teeth_lvl;
var db_old_liver_lvl;
var db_old_mouth_lvl; // Last Day Satisfaction
var db_old_posture_lvl; // Body Language
var db_old_waistSymmetry_lvl;
var db_old_waistline_lvl;
var db_old_stomach_lvl;
var db_old_tiredness_lvl;
var db_old_headache_lvl;

// Get the values for visual variables
var db_undefined;
var db_heart_lvl;
var db_skin_lvl;
var db_teeth_lvl;
var db_liver_lvl;
var db_mouth_lvl; 
var db_posture_lvl;
var db_waistSymmetry_lvl;
var db_waistline_lvl;
var db_stomach_lvl;
var db_tiredness_lvl;
var db_headache_lvl;

// DM: Save the values for the visual variables
var heart_lvl;
var skin_lvl;
var teeth_lvl;
var liver_lvl;
var mouth_lvl;
var posture_lvl;
var wrinkles_lvl;
var waistSymmetry_lvl;
var waistline_lvl;
var stomach_lvl;
var tiredness_lvl;
var headache_lvl;

var wrinkles_img; // used to define 1 of 3 wrinkle images based on wrinkles_lvl

////////////////////
//  IMAGE ASSETS  //
////////////////////

// Define the design asset arrays 
var leftLeg = ["leftleg01","leftleg_m_02","leftleg_m_03","leftleg_m_04","leftleg01","leftleg_w_03","leftleg_w_03","leftleg_w_05"];
var rightLeg = ["rightleg01","rightleg_m_02","rightleg_m_03","rightleg_m_04","rightleg01","rightleg_w_03","rightleg_w_03","rightleg_w_05"];
var leftUpperArm = ["leftupperarm01","leftupperarm01","leftupperarm01","leftupperarm_m_04","leftupperarm01","leftupperarm_w_03","leftupperarm_w_04","leftupperarm_w_03"];
var rightUpperArm = ["rightupperarm01","rightupperarm01","rightupperarm01","rightupperarm_m_04","rightupperarm01","rightupperarm_w_03","rightupperarm_w_04","rightupperarm_w_03"];
var leftArm = ["leftarm01","leftarm01","leftarm01","leftarm_m_04","leftarm01","leftarm_w_03","leftarm_w_03","leftarm_w_03"];
var rightArm = ["rightarm01","rightarm01","rightarm01","rightarm_m_04","rightarm01","rightarm_w_03","rightarm_w_03","rightarm_w_03"];
var hip = ["hip_m_01","hip_m_01","hip_m_01","hip_m_01","hip_w_02","hip_w_03","hip_w_04","hip_w_05"];
var chest = ["chest_m_01","chest_m_02","chest_m_03","chest_m_01","chest_w_02","chest_w_03","chest_w_04","chest_w_03"];
var head = ["head_m_01","head_m_01_highbmi","head_m_01_lowbmi","head_w_01","head_w_01_highbmi","head_w_01_lowbmi"];
var neck = ["neck"];
var eyes = ["eyes01","eyes02"];
var eyeColors = ["saddlebrown","green","steelblue","#6ECFE5","seagreen","silver","peru"]; //https://www.w3schools.com/tags/ref_colornames.asp
var nose = ["nose01","nose02"];
var hair = ["hair_m_01_1_black","hair_m_01_2_brown","hair_m_01_3_lightbrown","hair_m_01_4_blonde",
			"hair_m_02_1_black","hair_m_02_2_brown","hair_m_02_3_lightbrown","hair_m_02_4_blonde",
			"hair_m_03_1_black","hair_m_03_2_brown","hair_m_03_3_lightbrown","hair_m_03_4_blonde",
			"hair_m_04_1_black","hair_m_04_2_brown","hair_m_04_3_lightbrown","hair_m_04_4_blonde",
			"hair_w_02_1_black","hair_w_02_2_brown","hair_w_02_3_lightbrown","hair_w_02_4_blonde",
			"hair_w_03_1_black","hair_w_03_2_brown","hair_w_03_3_lightbrown","hair_w_03_4_blonde",
			"hair_w_04_1_black","hair_w_04_2_brown","hair_w_04_3_lightbrown","hair_w_04_4_blonde"
			];
var beard = ["beard01","beard_02_1_black","beard_02_2_brown","beard_02_3_lightbrown","beard_02_4_blonde",
			"beard_03_1_black","beard_03_2_brown","beard_03_3_lightbrown","beard_03_4_blonde",
			"beard_04_1_black","beard_04_2_brown","beard_04_3_lightbrown","beard_04_4_blonde"
			];
var glasses = ["glasses01","glasses02","glasses03"];

var walkingstick = ["walkingstick"];
var agehats = ["grandpahat","grandmahat"];
var superhero = ["superhero"];


// Define the design asset array for visual variables
var heart = ["heart_lvl_1","heart_lvl_2","heart_lvl_3","heart_lvl_4","heart_lvl_5"];
var mouth = ["mouth_lvl_1","mouth_lvl_2","mouth_lvl_3","mouth_lvl_4","mouth_lvl_5"];
var liver = ["liver_lvl_1","liver_lvl_2","liver_lvl_3","liver_lvl_4","liver_lvl_5"];
var teethoverlay = ["teethoverlay01","teethoverlay02","teethoverlay03","teethoverlay04","teethoverlay05"];
var wrinkles = ["wrinkles_1","wrinkles_2","wrinkles_3"];
var eyecircles = ["eyecircles01","eyecircles02"];
var visualVariables = [heart,mouth,liver,teethoverlay,wrinkles,eyecircles];

var eyecircleTransparancy = [0.00,0.03,0.07,0.12,0.25];
var wrinklesTransparancy = [0.15,0.2,0.15,0.2,0.175,0.225,0.275,0.3,0.325,0.35]; 

////////////////////////
//  TUTORIAL FEATURE  //
////////////////////////

// Define tutorial assets not related to the body
var tutorialView = ["tutorialview01","tutorialview01"];
var tutorialMessage = ["tutorialmessage01","tutorialmessage02","tutorialmessage03","tutorialmessage04","tutorialmessage05","tutorialmessage06","tutorialmessage07","tutorialmessage08","tutorialmessage09","tutorialmessage10"];
var tutorialButton = ["tutorialbutton01","tutorialbutton02","tutorialbutton03"];
var tutorialAssets = [tutorialView,tutorialMessage,tutorialButton];

var namearrow = ["namearrow"];

////////////////////////
//  MESSAGES FEATURE  //
////////////////////////

// Define messages assets and variables
var healthMessage = "Wow! Ich fühle mich wie Superman! Ich fühle mich wie Superman! Mein Essen gestern war köstlich und wirklich sehr gesund. Ich kann das weiterführen. Der Zahnarzt wird sich freuen: Ich habe meinen Zuckerkonsum super im Griff.";
var messageActive = 0; // not active by default, activated after last-day transition
var speechbubble = ["speechbubble01","speechbubble02"];
var messageButton = ["messagebutton01"];

var	messageButtonX;
var	messageButtonY;
var	messageButtonWidth;
var	messageButtonHeight; 

/////////////////////////////////
//  EFFECT TRANSITION FEATURE  //
/////////////////////////////////

// Define effect transition animation assets and variables
var lastDayActive = 0;
var transitionActive = 0;
var transitionDone = 0;

var lastdayXAdj = 0;
var saltXAdj = 0;
var fvXAdj = 0;
var sugarXAdj = 0;
var alcoholXAdj = 0;

var lastdayYAdj = 0;
var saltYAdj = 0;
var fvYAdj = 0;
var sugarYAdj = 0;
var alcoholYAdj = 0;

var maxTransitionDelay = 3;
var curTransitionDelay = 0;
var transitionInterval = setInterval(updateTransitionDelay, 20000 / fps);

var ingredientInAnimation = 0;

var ingredients = ["salt", "sugar", "alcohol","fv","lastday"];
var lastDayOverview = ["lastday01","lastday02","lastday03"];
var lastDaySmiley = ["lastdaysmiley01","lastdaysmiley02","lastdaysmiley03"];
var replayButton = ["replay"];
var lastDayAssets = [ingredients,lastDayOverview,lastDaySmiley,replayButton];

// set variables for positioning
var lastDayOverviewX;
var lastDayOverviewY;
var lastDayOverviewWidth;

var replayButtonX;
var replayButtonY;
var replayButtonWidth;
var replayButtonHeight;

/////////////////////////////////
//  DETAILS ON DEMAND FEATURE  //
/////////////////////////////////

// Define Details on Demand (DoD) assets
var detailsOnDemand = ["dod_heart","dod_mouth","dod_liver","dod_teeth"];

// Set variables for details on demand
var heartDoD = ["heart",0,1];
var heartDoDMsg = ["Herz","Beeinflust durch:","- Salz","+ Obst und Gemüse"];
var liverDoD = ["liver",0,1];
var liverDoDMsg = ["Leber","Beeinflust durch:","- Alkohol",""];
var eyesDoD = ["eyes",0,0];
var eyesDoDMsg = ["Müdigkeit","Beeinflust durch:","+ Obst und Gemüse","- Zuckerzusatz"];
var mouthDoD = ["mouth",0,1];
var mouthDoDMsg = ["Zufriedenheit","Beeinflust durch:","> Letztes Tagesprotokoll",""];
var teethDoD = ["teeth",0,1];
var teethDoDMsg = ["Zähne","Beeinflust durch:","- Zuckersatz",""];
var postureDoD = ["posture",0,0];
var postureDoDMsg = ["Körperhaltung","Beeinflust durch:","> Gesamte Ernährung der letzten 4 Tage",""];

var showDoD = [heartDoD,liverDoD,mouthDoD,teethDoD,eyesDoD,postureDoD];


////////////////////////////////////////
//  BODY SIZE AND POSITION VARIABLES  //
////////////////////////////////////////

// Define height of body
var chestHeight;
var headHeight;
var upperBodyHeight;
  
var hipHeight;
var legHeight;
var lowerBodyHeight;
  
var upperArmHeight;
var neckHeight;
 
var bodyHeight;

// define body part positions
var rightArmX;
var rightArmY;
var rightArmRot = 0;
var rightArmRotX = 0;
var rightArmRotY = 0;

var rightUpperArmX;
var rightUpperArmY;
var rightUpperArmWidth;
var rightUpperArmHeight;
var rightUpperArmRot;

var rightArmRotBalance;

var leftArmX;
var leftArmY;
var leftArmRot;
var leftArmWidth;
var leftArmHeight;
var leftArmYAdj;

var leftUpperArmRot;
var leftUpperArmX;
var leftUpperArmY;
var leftUpperArmWidth;
var leftUpperArmHeight;

var rightLegRot;
var leftLegRot;

// Setup coordinates for click-events
var heartXPos;
var heartYPos;
var	heartWidth;
var	heartHeight;

var liverXPos;
var liverYPos;
var	liverWidth;
var	liverHeight;

var skinXPos;
var skinYPos;
var	skinWidth;
var	skinHeight;

var eyesXPos;
var eyesYPos;
var	eyesWidth;
var	eyesHeight;

var mouthXPos;
var mouthYPos;
var	mouthWidth;
var	mouthHeight;

var teethXPos;
var teethYPos;
var	teethWidth;
var teethHeight;

var wrinklesXPos;
var wrinklesYPos;
var	wrinklesWidth;
var wrinklesHeight;

var postureXPos;
var postureYPos;
var	postureWidth;
var postureHeight;

var hairCounter = 0;

///////////////////////////
//  BMI BODY STRETCHING  //
///////////////////////////

var bmiWidthAdjust = 0;
var bmiXAdjust = 0;

////////////////////
//  DATA LOADING  //
////////////////////
var avatarData = "";
var avatarNewValues = "";
var avatarOldValues = "";


////////////////////////////////////////
////////////////////////////////////////
//            FUNCTIONS               //
////////////////////////////////////////
////////////////////////////////////////


////////////////////
// PREPARE CANVAS //
////////////////////
// Prepares the HTML5 canvas and sets the key attributes
// - defines key variables for responsive image drawing based on screen size
// - checks for internet and server connection before calling function to load data
// - adds button event handlers
// - loads images
// - sets different variables depending on conditions (e.g. first view = tutorial)

function prepareCanvas(canvasDiv, canvasWidth, canvasHeight) {
	// Setup the canvas area
	canvas = document.createElement('canvas');
	canvas.setAttribute('width', canvasWidth);
	canvas.setAttribute('height', canvasHeight);
	canvas.setAttribute('id', 'canvas');
	
	// reduce canvas area to fit screen size
	w = canvas.width*0.8; // don't use full with to ensure that all elements fit on the screen
	h = canvas.height*0.95; // same for height
	
	// Divide vertical avatar area into the main sections
	topSection = h*0.12;
	botSection = h*0.12;
	avatarSection = h-topSection-botSection;
	
	y = h*0.20; // define the start position for avatar assets
	
	// Append the HTML5 canvas element to the canvasDiv div
	canvasDiv.appendChild(canvas);
	
	// Initialize canvas in IE8 
	if(typeof G_vmlCanvasManager != 'undefined') {
		canvas = G_vmlCanvasManager.initElement(canvas);
	}
	
	// Setup Canvas
	context = canvas.getContext("2d"); // get the 2d canvas context
    canvasLeft = canvas.offsetLeft,
    canvasTop = canvas.offsetTop,
	
	// load user related avatar variables from database 
	testInternetConnection = navigator.onLine;
	console.log(navigator.onLine);
	if (testInternetConnection) { // check if the internet connection is available
		loadData(); // load data from the server
		loadGeneralData(); // assign general data from server to variables
		loadAvatar(); // assign avatar data from server to variables
		loadVisualVariables(); // assign visual variable data from server to variables
		loadIngredientVariables(); // assign ingredient variable data from server to variables
	} else {
		error = 1;
		showError("nointernet");	
	}
	
	if (error === 0) { // load images only if no error appeared during loading
		// EVENTS //
		// Add event listener for `click` events.
		canvas.addEventListener('click', function(event) {
			var x = event.pageX - canvasLeft,
				y = event.pageY - canvasTop;
			
			checkButtonsClicked(x,y);

		}, false);

		canvas.addEventListener('touchend', function(event) {
			var x = event.touches[0].pageX - canvasLeft,
				y = event.touches[0].pageY - canvasTop;
			
			checkButtonsClicked(x,y);
		}, false);
		
		// activate tutorial if it is the first view of the avatar
		if (showTutorial === true) {
			tutorialActive = 1;
			eatActive = 0; // Deactivate eating animation during tutorial
			
			// load other tutorial assets
			loadImagesFromArray(tutorialAssets);
		} else {
			// remove the bottom area which is only used for the tutorial
			avatarSection = avatarSection + botSection;
		}	
		
		// AVATAR DATA SETUP BASED ON AVAILABLE DATA
		// Based on which data is available, the avatar of the 4 days from yesterday (old) is shown or the current avatar from the last 4 days (current)
		if (db_old_undefined === false) {
			console.log("old avatar loaded");
			updateAllVisualVariables("old"); // visual variables levels are set with the "old" avatar values
			lastDayActive = 1; // last day effect transition is activated as the old data is available
		} else if (db_undefined === false) {
			console.log("new avatar loaded");
			updateAllVisualVariables("current");  // visual variables levels are set with the "old" avatar values
			lastDayActive = 0; // last day effect transition is deactivated
			messageActive = 1; // message is activated
			eatActive = 1; // eat animation is activated (cannot interfere with last day effect transition)
		} else {
			error = 1;
			showError("noserver");
		}
		
		// WRINKLES CALCULATION (Extension: could be moved to the server)
		// define wrinkles level (15-24: lvl 1, 25-34: lvl 2, 35-44: lvl 3,...)
		wrinkles_lvl = Math.round((age-10)/10);
		
		// ensure that wrinkles_lvl is at least 1 or below 10
		if (wrinkles_lvl <= 0) { wrinkles_lvl = 1};
		if (wrinkles_lvl > 10 ) { wrinkles_lvl = 10};
		
		if (wrinkles_lvl <= 2) {
			wrinkles_img = 0;
		} else if (wrinkles_lvl <= 4) {
			wrinkles_img = 1;
		} else {
			wrinkles_img = 2;
		}		
		
		// LOAD ASSETS
		// load body assets
		loadBodyImages();
		
		// load assets for visual variables
		loadImagesFromArray(visualVariables);
		
		// load all assets for Last Day Overview + Animation
		loadImagesFromArray(lastDayAssets);
		
		// load all details on demand assets
		detailsOnDemand.forEach(function(entry) {
			loadImage(entry);
		});

		// load MISC assets
		eatAssets.forEach(function(entry) {
			loadImage(entry);
		});		
		
	}
}		


////////////////////
//  DATA LOADING  //
////////////////////
// Loads various data from the server

function loadData() {
  if (error === 0) {	
		// TODO Test request 
        $.get( "https://swissfoodtracker.azurewebsites.net/avatar/state/?key=e6ff76ce406999e8148573340a46401c99fc8f8c", function( data ) {
			//console.log("Status: " + status);
			console.log(data);
			
			// parse data in a object
			avatarData = data.general_data;
			avatarNewValues = data.new_values;
			avatarOldValues = data.old_values; //data_old_values;
			
			console.log("test1");
			console.log("avatar_data loaded");	
			console.log("test_1529");
		
        }).fail(function() { // if request was not successful
			error = 1;
			showError("noserver");	
		});
  }
}

// Loads visual variable data based on the data available on the server
function loadVisualVariables(){
  if (error === 0) {
	db_old_undefined = $.isEmptyObject(avatarOldValues); // checks if the old data is not empty
	db_undefined = $.isEmptyObject(avatarNewValues); // checks if current/new data is not empty
	
	if (db_old_undefined === false) {  // if defined
		db_old_heart_lvl = Math.round(avatarOldValues.visual_variables.heart_lvl);
		db_old_skin_lvl = Math.round(avatarOldValues.visual_variables.skin_lvl);
		db_old_teeth_lvl = Math.round(avatarOldValues.visual_variables.teeth_lvl);
		db_old_liver_lvl = Math.round(avatarOldValues.visual_variables.liver_lvl);
		db_old_mouth_lvl = Math.round(avatarOldValues.visual_variables.mouth_lvl);
		db_old_posture_lvl = Math.round(avatarOldValues.visual_variables.posture_lvl);
		db_old_tiredness_lvl = Math.round(avatarOldValues.visual_variables.tiredness_lvl);		
		db_old_headache_lvl;	
		
		console.log("old visual variable values set");
	}
	
	if (db_undefined === false) {
		db_heart_lvl = Math.round(avatarNewValues.visual_variables.heart_lvl);
		db_skin_lvl = Math.round(avatarNewValues.visual_variables.skin_lvl);
		db_teeth_lvl = Math.round(avatarNewValues.visual_variables.teeth_lvl);
		db_liver_lvl = Math.round(avatarNewValues.visual_variables.liver_lvl);
		db_mouth_lvl = Math.round(avatarNewValues.visual_variables.mouth_lvl); 
		db_posture_lvl = Math.round(avatarNewValues.visual_variables.posture_lvl);
		db_tiredness_lvl = Math.round(avatarNewValues.visual_variables.tiredness_lvl);
		db_headache_lvl;
		
		db_lastday_lvl = Math.round(avatarNewValues.visual_variables.last_day);
		
		healthMessage = avatarNewValues.message;
		
		console.log("new visual variable values set");
		// EXTENSION: add overal_lvl for trend
	}
	
	if (db_undefined === true) { // if current avatar data (average of the last 4 days) is not available, show error
		console.log("Failed: visual variable data not set");
		error = 1;
		showError("data"); 
	}
  }
}

// Loads ingredient data variables
function loadIngredientVariables(){
  if (error === 0) {
	var testEmptyObject = $.isEmptyObject(avatarNewValues.ingredient_levels); // test if ingredient_levels have been submitted
	if (testEmptyObject === false) { // if the object ingredient_levels is not empty, then
		db_salt_lvl = Math.round(avatarNewValues.ingredient_levels.Salt);
		db_sugar_lvl = Math.round(avatarNewValues.ingredient_levels.Sugar); 
		db_alcohol_lvl = Math.round(avatarNewValues.ingredient_levels.Alcohol); 
		db_fv_lvl = Math.round(avatarNewValues.ingredient_levels.FV); 
		
		console.log("ingredient variable data set");
	} else {
		console.log("Failed: ingredient variable data not set");
		error = 1;
		showError("data"); // improve data handling
	}
  }
}

// GET general user information
function loadGeneralData() {
  if (error === 0) {  
    var testEmptyObject = $.isEmptyObject(avatarData);
	if (testEmptyObject === false) {
		name = avatarData.first_name; // "Klaus";
		gender = avatarData.gender; // 0 = male, 1 = female
		if (gender === "Male") {gender = 0} else { gender = 1}; // transform gender in number
		age = calculateAge(avatarData.date_of_birth); // calculate age in years
		bodyweight = avatarData.weight; // body weight in KG
		bodysize = avatarData.height; // body size in cm
		calculateBMI();
		
		console.log("general variable data set");
	} else {
		console.log("Failed: general variable data not set");
		error = 1;
		showError("data"); // improve data handling				
	}
  }
}

// Load avatar customization data (e.g. hair type)
function loadAvatar(){
  if (error === 0) {
	var testEntry = avatarData.avatar_design.outfit_type; // load one of the variables of avatar_design
	if (testEntry == null) { // if the data cannot be loaded, just define a sample avatar dataset per gender
		if (gender === 1) {
			// use default avatar data for female
			outfit_type = 5;
			hair_type = 17;
			beard_type = 0;
			glasses_type = 0;
			eyecolor_type = 1;			
		} else {
			// use default avatar data for male
			outfit_type = 1;
			hair_type = 5;
			beard_type = 1;
			glasses_type = 1;
			eyecolor_type = 2;
		}			
	} else { 
		// get avatar customization values from server
		outfit_type = parseInt(avatarData.avatar_design.outfit_type); 
		hair_type = parseInt(avatarData.avatar_design.hair_type);
		if (avatarData.avatar_design.beard_type == null) { //set beard to 0 if undefined "" 	
			beard_type = 0; 
		} else {
			beard_type = parseInt(avatarData.avatar_design.beard_type); 		
		}
		glasses_type = parseInt(avatarData.avatar_design.glasses_type);
		eyecolor_type = parseInt(avatarData.avatar_design.eyecolor_type);
		showTutorial = avatarData.avatar_design.show_tutorial;
	}

	// DEFINE gender-based variables
	eyes_type = gender+1;
	nose_type = gender+1;
	
	// DEFINE detailes avatar customization values (lower level)
	// upper body
	vChest = outfit_type;
	vLeftUpperArm = outfit_type;
	vRightUpperArm = outfit_type;
	vLeftArm = outfit_type;
	vRightArm = outfit_type;
	
	// lower body
	vLeftLeg = outfit_type;
	vRightLeg = outfit_type;
	vHip = outfit_type;
	
	// other variables	
	console.log("head:" + head_type);
	vHead = head_type;
	vEyes = eyes_type;
	vNose = nose_type;
	vHair = hair_type;
	vBeard = beard_type;
	vGlasses = glasses_type;
	vShoes = shoes_type;
	vSkinColor = skincolor_type;
	vEyeColor = eyecolor_type;	
  }
}

function calculateBMI(){
	var	bmi = bodyweight/(bodysize/100*bodysize/100); // calculate BMI
	console.log("BMI " + bmi);
	
	// define widthAdjust based on BMI
	if (bmi < 18.5){
		//underweight adjustment
		bmiWidthAdjust = -w*0.01;
		bmiXAdjust = -bmiWidthAdjust/2;
		head_type = (gender*3)+3;
	} else if (bmi < 25) {
		//no adjustment with normal weight
		head_type = gender*3+1;
	} else {
		//overweight adjustment
		bmiWidthAdjust = w*0.02;
		bmiXAdjust = -bmiWidthAdjust/2;
		head_type = (gender*3)+2;
	}
}

function calculateAge(dateStr) {
    var today = new Date();
    var birthDate = new Date(dateStr);
    var age = today.getFullYear() - birthDate.getFullYear();
    var month = today.getMonth() - birthDate.getMonth();
	
    if (month<0 || (today.getDate() < birthDate.getDate()) && month === 0) { age--; }
	
    return age;
}

///////////////////////////////////////
//  UPDATES OF VARIABLES ON RUNTIME  //
///////////////////////////////////////

function updateVisualVariable(ingredient){
	switch (ingredient) {
		case "salt":
			heart_lvl = db_heart_lvl;
			break;
			
		case "sugar":
			teeth_lvl = db_teeth_lvl;
			break;
			
		case "alcohol":
			liver_lvl = db_liver_lvl;
			break;
			
		case "fv":
			tiredness_lvl = db_tiredness_lvl;				
			break;
			
		case "lastday":
			posture_lvl = db_posture_lvl; 
			break;
			
		default:
			console.log("updateVisualVariable: ingredient not know");
	}		
}

function updateAllVisualVariables(dataset){
	switch (dataset) {
		case "current":
			heart_lvl = db_heart_lvl;
			skin_lvl = db_skin_lvl;
			teeth_lvl = db_teeth_lvl;
			liver_lvl = db_liver_lvl;
			mouth_lvl = db_mouth_lvl;
			posture_lvl = db_posture_lvl;
			waistSymmetry_lvl = db_waistSymmetry_lvl;
			waistline_lvl = db_waistline_lvl;
			stomach_lvl = db_stomach_lvl;
			tiredness_lvl = db_tiredness_lvl;
			headache_lvl = db_headache_lvl;	
			break;
		
		case "old":
			heart_lvl = db_old_heart_lvl;
			skin_lvl = db_old_skin_lvl;
			teeth_lvl = db_old_teeth_lvl;
			liver_lvl = db_old_liver_lvl;
			mouth_lvl = db_old_mouth_lvl;
			posture_lvl = db_old_posture_lvl;
			waistSymmetry_lvl = db_old_waistSymmetry_lvl;
			waistline_lvl = db_old_waistline_lvl;
			stomach_lvl = db_old_stomach_lvl;
			tiredness_lvl = db_old_tiredness_lvl;
			headache_lvl = db_old_headache_lvl;			
			break;
			
		case "ideal":
			heart_lvl = 1;
			skin_lvl = 1;
			teeth_lvl = 1;
			liver_lvl = 1;
			mouth_lvl = 1;
			posture_lvl = 1;
			waistSymmetry_lvl = 1;
			waistline_lvl = 1;
			stomach_lvl = 1;
			tiredness_lvl = 1;
			headache_lvl = 1;
			break;		

		default:
			//console.log("not updated");
	}
}


/////////////////////////////////
//        IMAGE LOADING        //
/////////////////////////////////

function loadBodyImages() {
	// load images into the canvas based on the selected values
	loadImage(leftLeg[vLeftLeg-1]);
	loadImage(rightLeg[vRightLeg-1]);
	loadImage(hip[vHip-1]);
	loadImage(chest[vChest-1]);
	loadImage(leftUpperArm[vLeftUpperArm-1]);
	loadImage(rightUpperArm[vRightUpperArm-1]);
	loadImage(leftArm[vLeftArm-1]);
	loadImage(rightArm[vRightArm-1]);
	loadImage(nose[vNose-1]);
	loadImage(hair[vHair-1]);
	loadImage(neck[0]);

	if (vBeard != 0) {
		loadImage(beard[vBeard-1]);		
	}
	
	loadImage(eyes[vEyes-1]);
	loadImage(head[vHead-1]);
	
	loadImage(wrinkles[wrinkles_img]);
	
	if (vGlasses != 0) {
		loadImage(glasses[vGlasses-1]);
	}
	
	loadImage(walkingstick[0]);
	loadImage(agehats[0]);
	loadImage(agehats[1]);
	loadImage(superhero[0]);
	loadImage(namearrow[0]);
	loadImage(speechbubble[0]);
	loadImage(messageButton[0]);
}

function loadImagesFromArray(array){
	array.forEach(function(arrayelement) {
		arrayelement.forEach(function(entry) {
			loadImage(entry);
		});
	});	
}

function loadImage(name) {
  images[name] = new Image();
  images[name].onload = function() { 
	  resourceLoaded();
  }
  images[name].src = "{{STATIC_URL}}images/" + name + ".png";
  images[name].id = name;
}

function resourceLoaded() {

  numResourcesLoaded += 1;
  
  // if all resources are loaded
  if(numResourcesLoaded === totalResources && error === 0) {
	  
	// start drawing cycle
	setInterval(redraw, 1000 / fps);	
  }
}


/////////////
// DRAWING //
/////////////

// Key drawing function which is constantly called to redraw the canvas scene
function redraw() {		

	if (error === 0){
		
	  canvas.width = canvas.width; // clears the canvas 
	  
	  console.log("tutorialActive: " + tutorialActive);
	  console.log("lastDayActive: " + lastDayActive);
	  console.log("transitionActive: " + transitionActive);
	  console.log("transitionDone: " + transitionDone);
	  console.log("messageActive: " + messageActive);
	  console.log("eatActive: " + eatActive);
	  console.log("ingredientInAnimation: " + ingredientInAnimation);
	  
	  if (redrawCounter === 1) {
		    // start intervals for animations
		    eatTimer = setInterval(updateEat, eatUpdateTime);
 
			// initiate eye height for blinking
			maxEyeHeight = getImgRespHeight(images[eyes[vEyes-1]],w/(4.9+(tiredness_lvl-1)/2));
			curEyeHeight = maxEyeHeight;			
			
			// initiate mouth height for chewing
			curMouthHeight = mouthHeight;
	  }

	  // Get relative height of the images
	  calculateBodyHeight();
	  
		if (bodyHeight > avatarSection) {
			  do {
				w = w - 5;
				calculateBodyHeight();
				//console.log("w reduced")
			  }
			  while (bodyHeight > avatarSection);
			  fillButtonsArray();
		} else if (bodyHeight+11 < avatarSection) {
			  do {
				w = w + 5;
				calculateBodyHeight();
				//console.log("w increased")
			  }
			  while (bodyHeight < avatarSection);
			  fillButtonsArray();
		}

	  // Define leftOffset to center elements and allow enough space in front of the avatar
	  leftOffset = (canvas.width-w)/2.1;

	  // Define avatar coordinates and rotation
	  rightArmX = w*0.66;
	  rightArmY = y+headHeight-neckHeight/2+upperArmHeight/1.3-curBreath;
	  rightArmWidth = w/14;
	  rightArmHeight = getImgRespHeight(images[rightArm[vRightArm-1]],w/14);
	  rightArmRot = 0;
	  
	  rightUpperArmX = w*0.56-(gender*w*0.015);
	  rightUpperArmY = y+headHeight-curBreath-neckHeight/2;
	  rightUpperArmWidth = w/15;
	  rightUpperArmHeight = getImgRespHeight(images[rightUpperArm[vRightUpperArm-1]],w/15);
	  rightUpperArmRot = 330;
	  
	  leftArmX = w*0.22;
	  leftArmY = y+headHeight-neckHeight/2+upperArmHeight/1.3-leftArmYAdj-curBreath;
	  leftArmWidth = w/14;
	  leftArmHeight = getImgRespHeight(images[leftArm[vLeftArm-1]],w/14); 
	  
	  leftUpperArmX = w*0.37+(gender*w*0.015);
	  leftUpperArmY = y+headHeight-curBreath-neckHeight/2;
	  leftUpperArmWidth;
	  leftUpperArmHeight;
	  
	  // define buttons coordinates which might not be loaded from the beginning
	    messageButtonX = leftOffset+w*0.05;
		messageButtonY = w*0.36;
		messageButtonWidth = w/5;
		messageButtonHeight = getImgRespHeight(images[messageButton[0]],w/5); 
	  
	  // define body language (visual variable posture) - EXTENSION: currently hardcoded, could be improved in the future to be more dynamic (joints behavior)
	  switch (posture_lvl) {
		  case 1:
			leftUpperArmRot = 120;
			leftArmRot = 160+curWaveRot*1.5;
			leftArmX = w*0.23+(gender*w*0.015);
			leftArmYAdj = w*0.23;	 
			waveIncrement = 1.5;

			tarEatRotation = 170;
			
			rightLegRot = -40;
			leftLegRot = 0;
		
			break;
			
		  case 2:
			leftUpperArmRot = 70; 
			leftArmRot = 140+curWaveRot;
			leftArmX = w*0.22+(gender*w*0.015);
			leftArmYAdj = w*0.10;
			waveIncrement = 1;		

			rightUpperArmRot = 320;
			rightArmRot = 15;
			tarEatRotation = 150;			
			
			rightLegRot = -20;
			break;
			
		  case 3:
			leftUpperArmRot = 60;
			leftArmRot = 344;
			leftArmX = w*0.23+(gender*w*0.015);
			leftArmYAdj = w*0.07;
			
			rightUpperArmRot = 300;
			rightArmRot = 15;
			tarEatRotation = 140;
			
			rightLegRot = 0;
			leftLegRot = 0;
			break;	  
		  
		  case 4:
			leftUpperArmRot = 30;
			leftArmRot = 0;
			leftArmX = w*0.28+(gender*w*0.015);
			leftArmYAdj = w*0.03;
			
			rightLegRot = 0;
			leftLegRot = 0;
			break;
			
		  case 5:
			leftUpperArmRot = 30;
			leftArmRot = 80;
			leftArmX = w*0.28+(gender*w*0.015);
			leftArmYAdj = w*0.02;
			
			rightLegRot = 0;
			leftLegRot = 0;
			break;
		  
		  default:
		  
	  }  
	  
	  if (rightUpperArmRot > 300) {
		  rightArmRotBalance = (90-(rightUpperArmRot-270))/90*1.2;
	  } else if (rightUpperArmRot > 270) {
		  rightArmRotBalance = (90-(rightUpperArmRot-270))/90;
	  } else if (rightUpperArmRot > 180) {
		  rightArmRotBalance = (rightUpperArmRot-180)/90;
	  }
  
	  drawAvatar();

	  // draw animation assets
	  if (eat === 0) { // when eating
		  // draw fruit/vegetable on hand

		  // Extension: Should be improved to automatically target the mouth x and y position (currently hardcoded)
		  if (curEatRotation+rightArmRot > 90) { // if arm is close to mouth, draw it flying toward the mouth
			  if (eatAdjustX < w*0.10) {
				eatAdjustX += w*0.015;
				eatAdjustY = w*0.01;
			  }
			  if (rightArmRot === 0) {
				eatAdjustY = w*0.05;
			  }
			  drawImageRot(images[eatAssets[eatAssetActive]], rightUpperArmX+(rightUpperArmHeight*rightArmRotBalance)+leftOffset-eatAdjustX, rightUpperArmY + (rightUpperArmHeight*(1-rightArmRotBalance))-eatAdjustY, w/14, getImgRespHeight(images[rightArm[vRightArm-1]],w/14),rightArmRot + curEatRotation);

		 } else {
			  // else draw eatAsset exactly on arm
			  eatAdjustX = 0;
			  eatAdjustY = 0;
		      drawImageRot(images[eatAssets[eatAssetActive]], rightUpperArmX+(rightUpperArmHeight*rightArmRotBalance)+leftOffset, rightUpperArmY + (rightUpperArmHeight*(1-rightArmRotBalance)), w/14, getImgRespHeight(images[rightArm[vRightArm-1]],w/14),rightArmRot + curEatRotation);
		  }

	  }
	  
	  if (chewing === 1) {
		  chew();
	  } else {
		  // if not chewing, ensure mouth is proper height
		  curMouthHeight = mouthHeight;
	  }
	  
	  if (tutorialActive === 1) {
		  messageActive = 0;
		  eatActive = 0;
		  drawTutorial(tutorialStep);
		  if (tutorialStep === 2) {			  
			  updateAllVisualVariables("ideal");
		  } else if (db_old_undefined === false) {
			  updateAllVisualVariables("old");
		  } else if (db_undefined === 1) {
			  updateAllVisualVariables("current");
		  }
	  }  
	  
	  if (transitionActive === 1) {
		  eatActive = 0;
		  eyesNotUpdated = 1;
		  eyeOpenTime = 0;
	  }
	  
	  if (lastDayActive === 1 && tutorialActive === 0) {
		  // disable eat (healthy behavior) animation while drawing last day animation
		  drawLastDay();
		  if (transitionActive === 1) {
			  eatActive = 0;
			  eyesNotUpdated = 1;
			  eyeOpenTime = 0;
		  }	else {
			  // draw replay button after the transition
			  drawImage(images[replayButton[0]],lastDayOverviewX+lastDayOverviewWidth/3,lastDayOverviewY+w*0.01+getImgRespHeight(images[lastDayOverview[0]],lastDayOverviewWidth),w/20);
		  }
	  
	  }
	  
	  if (messageActive === 1) {
		drawMessages();
	  }
	  
	  drawDetailsOnDemand();
	  
	  drawButtons();  

	  if (eyesNotUpdated === 1) {
		// initiate eye height for blinking
		maxEyeHeight = getImgRespHeight(images[eyes[vEyes-1]],w/(4.9+(tiredness_lvl-1)/2));
		curEyeHeight = maxEyeHeight;	
		
		eyesNotUpdated = 0;
	  }	  
	  
	}
}

// Draws a image with relative height
function drawImage(img,xPos,yPos,width){
	context.drawImage(img, xPos, yPos, width, getImgRespHeight(img,width));
}

// Draws a rotated image
function drawImageRot(img,x,y,width,height,deg){
  context.save();
  
  // set the origin to the top middle part of the image (e.g. start of the arm);
  context.translate(x+width/2,y+height/20);
  
  // rotate the canvas around the origin
  context.rotate(deg*Math.PI/180);
  
  context.translate(-x-width/2,-y-height/20);
  
  // draw image
  context.drawImage(img, x, y, width, height);
  
  // reset canvas 
  context.restore();
}

// Draws detail on demand assets and details
function drawDetailsOnDemand(){
	var heightPreviousDoD = 0;
	showDoD.forEach(function(variable, i) {
		if (variable[1] === 1) {
			heightPreviousDoD = drawDoD(variable[0],variable[2],i,heightPreviousDoD);
		}
	});	
}

// Draws messages in a speech bubble
function drawMessages(){
	
	// draw messagebutton
	drawImage(images[messageButton[0]],messageButtonX,messageButtonY,messageButtonWidth);
	
	// draw speech bubble
	drawImage(images[speechbubble[0]],leftOffset,w*0.065,w/1.05);		
	
	// EXTENSION: split up the messages in multiple messages which appear after each other with a click (if longer than 250)
	
	// split message text 
	var maxLen = 250; // define the maximum length of a message string until it is cut off
	var input = healthMessage.substring(0, maxLen);; // take message as input
	var strLen = 42;
	var currItem = strLen;
	var prevItem = 0;
	
	output = [];

	while (input[currItem]) {
		if (input[currItem++] == ' ') {
			output.push(input.substring(prevItem,currItem));
			prevItem = currItem;
			currItem += strLen;
		}
	}
	output.push(input.substr(prevItem));  	
	
	// write message text
	context.font = ""+w*0.038+"px sans-serif";
	context.fillStyle = '#000';
	output.forEach(function(segment,i) {
		context.fillText(segment, leftOffset+w*0.03, w*0.06+w*0.06+(w*0.043)*i); 	
	});

}

// Draws last day "effect transition" animation
function drawLastDay(){

	var lastDaySmileyImg;
	
	lastDayOverviewX = leftOffset+w*0.8;
	lastDayOverviewY = w*0.52;
	lastDayOverviewWidth = w/7.5;

	replayButtonX = lastDayOverviewX+lastDayOverviewWidth/3;
	replayButtonY = lastDayOverviewY+getImgRespHeight(images[lastDayOverview[0]],lastDayOverviewWidth);
	replayButtonWidth = w/20;	
	replayButtonHeight = getImgRespHeight(images[replayButton[0]],replayButtonWidth);
	
	// title
	context.font = "bold "+w*0.03+"px sans-serif";
	context.fillStyle = '#000';
	context.fillText("Letzter", lastDayOverviewX, lastDayOverviewY-w*0.04); 
	context.fillText("Tag", lastDayOverviewX, lastDayOverviewY-w*0.01); 
	
	// draw overview asset based on the last day value
	switch (db_lastday_lvl) {
		case 1:
		case 2:
			drawImage(images[lastDayOverview[0]],lastDayOverviewX,lastDayOverviewY,lastDayOverviewWidth);
			lastDaySmileyImg = 0;
			break;
		case 3:
			drawImage(images[lastDayOverview[1]],lastDayOverviewX,lastDayOverviewY,lastDayOverviewWidth);
			lastDaySmileyImg = 1;
			break;
		case 4:
		case 5:
			drawImage(images[lastDayOverview[2]],lastDayOverviewX,lastDayOverviewY,lastDayOverviewWidth);
			lastDaySmileyImg = 2;
			break;		
			
		default:
	}
	
	ingredients.forEach(function(ingredient,i){
			var level = window["db_" + ingredients[i] + "_lvl"];
			var size = w*0.02*(1+level);
			var topSpace = (5-level)*w*0.015;
			var leftAdj = ((5-level)*w*0.01);
			
			if (ingredients[i] === "fv") {
				size = w*0.02*(7-level);
				topSpace = (level-1)*w*0.015;
				leftAdj = (level-1)*w*0.01;		
			}
			if (ingredients[i] === "lastday") {
				size = w*0.02*4.5;
				topSpace = -w*0.55;
				leftAdj = w*0.015;		
			}			

			var ingredientXPos = lastDayOverviewX+leftAdj+w*0.005;
			var ingredientYPos = lastDayOverviewY+w*0.125+(i*w*0.11)+topSpace;
			
			// draw each ingredient, the size and positioning is depending on the lvl (the lower, the larger)
			if (ingredients[i] === "lastday") {
				drawImage(images[lastDaySmiley[lastDaySmileyImg]],ingredientXPos,ingredientYPos,size);
			} else if (ingredients[i] === "alcohol" && level === 1){
					// if no alcohol was consumed
					drawImage(images[ingredients[i]],ingredientXPos,ingredientYPos,size);
					
					// draw a rotated cross on the alcohol symbol
					context.save();
					context.translate(ingredientXPos+w*0.035,ingredientYPos);
					context.rotate(130*Math.PI/180);
					context.translate(-ingredientXPos-w*0.035,-ingredientYPos);
					context.fillStyle = "red";
					context.fillRect(ingredientXPos+w*0.035, ingredientYPos, size, w*0.003);
					context.restore();
			} else {
				drawImage(images[ingredients[i]],ingredientXPos,ingredientYPos,size);					
			}
		
		if (transitionActive === 1) {
		
		if (curTransitionDelay > maxTransitionDelay) {
			if (ingredientInAnimation === i) { 
						if ((ingredientXPos+window[ingredients[i]+"XAdj"]) > mouthXPos+5){
							window[ingredients[i]+"XAdj"] -= 5;
						} 
						if ((ingredientYPos+window[ingredients[i]+"YAdj"]) > mouthYPos+5){
							window[ingredients[i]+"YAdj"] -= 5;
						}
						// Info: if overview is centered, this also needs to take into account for a range
						if (((ingredientYPos+window[ingredients[i]+"YAdj"]) < mouthYPos+5) && ((ingredientXPos+window[ingredients[i]+"XAdj"]) < mouthXPos+5)) {
							ingredientInAnimation = i+1;
							updateVisualVariable(ingredients[i]);
							chewing = 1;
							if (ingredientInAnimation === ingredients.length) {
								// set to transition done and show message
								transitionActive = 0;
								transitionDone = 1;
								messageActive = 1;
								eatActive = 1;		
								
								// reset X and Y adjustment
								lastdayXAdj = 0;
								saltXAdj = 0;
								fvXAdj = 0;
								sugarXAdj = 0;
								alcoholXAdj = 0;
								lastdayYAdj = 0;
								saltYAdj = 0;
								fvYAdj = 0;
								sugarYAdj = 0;
								alcoholYAdj = 0;
																
								updateAllVisualVariables("current"); // ensure that all visual variables are updated to the current values	
	
								// initiate eye height for blinking
								maxEyeHeight = getImgRespHeight(images[eyes[vEyes-1]],w/(4.9+(tiredness_lvl-1)/2));
								curEyeHeight = maxEyeHeight;	

								// initiate mouth height for chewing
								curMouthHeight = mouthHeight;
								}
						}
			}
			
			if (ingredientInAnimation === i) { 
				if (ingredients[i] === "lastday") {
					drawImage(images[lastDaySmiley[lastDaySmileyImg]],ingredientXPos+window[ingredients[i]+"XAdj"],ingredientYPos+window[ingredients[i]+"YAdj"],size);
				} else if (ingredients[i] === "alcohol" && level === 1){
					// if no alcohol was consumed
					drawImage(images[ingredients[i]],ingredientXPos+window[ingredients[i]+"XAdj"],ingredientYPos+window[ingredients[i]+"YAdj"],size);
					
					// draw a rotated cross on the alcohol symbol
					context.save();
					context.translate(ingredientXPos+window[ingredients[i]+"XAdj"]+w*0.035,ingredientYPos+window[ingredients[i]+"YAdj"]);
					context.rotate(130*Math.PI/180);
					context.translate(-ingredientXPos-window[ingredients[i]+"XAdj"]-w*0.035,-ingredientYPos-window[ingredients[i]+"YAdj"]);
					context.fillStyle = "red";
					context.fillRect(ingredientXPos+window[ingredients[i]+"XAdj"]+w*0.035, ingredientYPos+window[ingredients[i]+"YAdj"], size, w*0.003);
					context.restore();
					
				} else {
					drawImage(images[ingredients[i]],ingredientXPos+window[ingredients[i]+"XAdj"],ingredientYPos+window[ingredients[i]+"YAdj"],size);
				}		
				
			} 
		}
		}
	});
	
	if (transitionDone === 0) {
		transitionActive = 1;
	}
	
}

// Draws details on demand based on the position of the visual variable positions
function drawDoD(variable,hasimg,i,heightPreviousDoD) { // to ensure skin is not active,i,heightPreviousDoD) 

			var rectX = window[variable+"XPos"]; 
			var rectY = window[variable+"YPos"]+window[variable+"Height"]+heightPreviousDoD+w*0.01+curBreath;//yAdj;
			
			if (variable === "eyes"){
				rectY = rectY - (maxEyeHeight-curEyeHeight)/1.5;
			}

			var contentX = rectX+w*0.02;
			var contentY = rectY+w*0.055;
			
			// draw background
			context.fillStyle = "#FFF";
			context.fillRect(rectX, rectY, w/2.2, w/(5-hasimg*2));
			
			context.lineWidth="2";
			context.strokeStyle ="#000";
			context.strokeRect(rectX, rectY, w/2.2, w/(5-hasimg*2));
			
			//// write text
			// title
			context.font = "bold "+w*0.04+"px sans-serif";
			context.fillStyle = '#000';
			context.fillText(window[variable+"DoDMsg"][0], contentX, contentY); 

			// explanation
			//context.font = w*0.025+"px sans-serif";
			//context.fillStyle = '#000';
			//context.fillText(window[variable+"DoDMsg"][1], contentX, contentY+w*0.04); 			

			// factor 1
			if (window[variable+"DoDMsg"][2].charAt(0) === "-"){
				context.fillStyle = '#CC0000';
			} else if (window[variable+"DoDMsg"][2].charAt(0) === "+"){
				context.fillStyle = '#006600';
			} else {
				context.fillStyle = '#000';
			}
			context.font = "bold " + w*0.03+"px sans-serif";
			context.fillText(window[variable+"DoDMsg"][2], contentX, contentY+w*0.04); 	

			// factor 2
			if(window[variable+"DoDMsg"][3].charAt(0) === "-"){
				context.fillStyle = '#CC0000';
			} else if (window[variable+"DoDMsg"][3].charAt(0) === "+"){
				context.fillStyle = '#006600';
			} else {
				context.fillStyle = '#000';
			}
			context.font = "bold " + w*0.03+"px sans-serif";
			context.fillText(window[variable+"DoDMsg"][3], contentX, contentY+w*0.8); 				

			if (hasimg === 1) { // if image is available			
				// text "gesund" + "ungesund"
				context.fillStyle = '#006600';
				context.font = w*0.025+"px sans-serif";
				context.fillText("gesund", contentX, contentY+(w/3)*0.52); 	

				context.fillStyle = '#CC0000';
				context.font = w*0.025+"px sans-serif";
				context.fillText("ungesund", contentX+w/3.25, contentY+(w/3)*0.52); 	
			
				// visual variable guide
				drawImage(images["dod_"+variable],contentX,contentY+(w/3)*0.56,w/2.35);					
			}
			
			// return hight of DoD
			return w/(5-hasimg*2);

}

// Draws tutorial messages and buttons
function drawTutorial(step){
	var tutButtonX = leftOffset+w*0.05;
	var tutButtonY = topSection+avatarSection;
	var tutButtonWidth = w*0.9;
	
	switch (step) {
		case 1:
		drawImage(images[tutorialMessage[step-1]],leftOffset, topSection-getImgRespHeight(images[tutorialMessage[step-1]],w), w);
		drawImage(images[tutorialButton[0]],tutButtonX,tutButtonY,tutButtonWidth);
		break;
		
		case 2:
		drawImage(images[tutorialMessage[step-1]],leftOffset, topSection-getImgRespHeight(images[tutorialMessage[step-1]],w), w);
		drawImage(images[tutorialButton[1]],tutButtonX,tutButtonY,tutButtonWidth);
		break;
		
		case 3:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.22, topSection+avatarSection-w*0.5, w/1.8);
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;

		case 4:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.265, w*0.54, w/1.8);
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;

		case 5:
		drawImage(images[tutorialMessage[step-1]],leftOffset-w*0.03, w*0.37, w/2.3); // Obst+Gemüse
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;
		
		case 6:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.19, w*0.66, w/1.7); // Zähne
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;

		case 7:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.15, w*1.03, w/1.7); // Leber
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;		

		case 8:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.01, w*0.53, w/2.4); // Zufriedenheit/Mund
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;

		case 9:
		drawImage(images[tutorialMessage[step-1]],leftOffset, w*0.4, w); // Last Day Overview
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;
		
		case 10:
		drawImage(images[tutorialMessage[step-1]],leftOffset+w*0.14, w*0.8, w/1.4); // Jetzt bist du dran!
		drawImage(images[tutorialButton[2]],tutButtonX,tutButtonY,tutButtonWidth);
		break;
		
		case 11:
		tutorialActive = 0;
		curTransitionDelay = 0;
		avatarSection = avatarSection + botSection;
		updateVisualVariable("fv");
		break;		
		
		default:
		//console.log("default: drawTutorial");
	    
	}
}

// Draws avatar (body) assets and name
function drawAvatar(){
	
  // draw name and arrow
  var nameDisplay = name + " (" + (age+10) + " Jahre)";
  context.font = "small-caps "+w*0.04+"px sans-serif";
  context.fillStyle = '#6699FF';
  context.fillText(nameDisplay, leftOffset+w*0.46-(w*(nameDisplay.length-3)/100), w*0.10); 
  drawImage(images[namearrow[0]],leftOffset+w*0.465, w*0.13+curBreath/2, w/16);

  // draw accessories behind body);
  if (posture_lvl === 1) {
	  context.drawImage(images[superhero[0]], w*0.08+leftOffset+curBreath/2, y+headHeight-neckHeight/1.3-curBreath, w/1.6, getImgRespHeight(images[superhero[0]],w/1.6));
  }  
  
  // draw body parts
  drawImageRot(images[rightLeg[vRightLeg-1]], w*0.53+leftOffset, y+upperBodyHeight*1.13-neckHeight, w/7.5, getImgRespHeight(images[rightLeg[vRightLeg-1]],w/7.5),rightLegRot);
  drawImageRot(images[leftLeg[vLeftLeg-1]], w*0.33+leftOffset, y+upperBodyHeight*1.13-neckHeight, w/7.5, getImgRespHeight(images[leftLeg[vLeftLeg-1]],w/7.5),leftLegRot);
  context.drawImage(images[hip[vHip-1]], w*0.332+leftOffset+bmiXAdjust, y+upperBodyHeight-neckHeight, w/3+bmiWidthAdjust, getImgRespHeight(images[hip[vHip-1]],w/3));
  
  //// define positions of visual variables
  // heart
  heartXPos = w*0.5+leftOffset;
  heartYPos = y+headHeight+w/25-curBreath;
  heartWidth = w/12;
  heartHeight = getImgRespHeight(images[heart[heart_lvl-1]],w/12);
  // liver
  liverXPos = w*0.415+leftOffset;
  liverYPos = y+headHeight+chestHeight/2.1-curBreath;
  liverWidth = w/9;
  liverHeight = getImgRespHeight(images[liver[liver_lvl-1]],w/9);
  // skin  
  skinXPos = w*0.35+leftOffset;
  skinYPos = y-curBreath;
  skinWidth = w/3.5;
  skinHeight = headHeight;    
  // eyes
  eyesXPos = w*0.39+leftOffset;
  eyesYPos = y+headHeight/4.4+(maxEyeHeight-curEyeHeight)/1.5+((tiredness_lvl-1)/600*w)-curBreath,
  eyesWidth = w/4.9;
  eyesHeight = getImgRespHeight(images[eyes[vEyes-1]],w/4.9); 
  // mouth
  mouthXPos = w*0.442+leftOffset;
  mouthYPos = y+headHeight/1.95-curBreath;
  mouthWidth = w/10;
  mouthHeight = getImgRespHeight(images[mouth[mouth_lvl-1]],w/10);  
  // teeth
  teethXPos = mouthXPos;
  teethYPos = mouthYPos;
  teethWidth = mouthWidth;
  teethHeight = mouthHeight;
  // wrinkles
  wrinklesXPos = skinXPos;
  wrinklesYPos = skinYPos;
  wrinklesWidth = skinWidth;
  wrinklesHeight = skinHeight;
  // posture
  postureXPos = leftOffset;
  postureYPos = y;
  postureWidth = 0;
  postureHeight = 0;
  

  // draw neck below head but above 
  //context.drawImage(images[neck[0]], skinXPos+skinWidth/2.8-w*0.01,y+headHeight/1.21-curBreath,w*0.08+w*0.02,w*0.07);
  //context.drawImage(images[neck[0]], skinXPos+skinWidth/2.8,y+headHeight/1.21-curBreath,w*0.08,w*0.07);
  
  // draw head with visual variable "skin saturation" - EXTENSION: add different head types
  context.save();
  context.globalAlpha = 1-((skin_lvl-1)/12);
  context.drawImage(images[head[vHead-1]], skinXPos, skinYPos, skinWidth, skinHeight);  
  context.restore();	

  // draw left upper arm (with rotation)
  drawImageRot(images[leftUpperArm[vLeftUpperArm-1]], leftUpperArmX+leftOffset+bmiXAdjust/1.5, leftUpperArmY, w/15, getImgRespHeight(images[leftUpperArm[vLeftUpperArm-1]],w/15),leftUpperArmRot);    
  
  // draw right upper arm (with rotation);
  drawImageRot(images[rightUpperArm[vRightUpperArm-1]], rightUpperArmX+leftOffset-bmiXAdjust/1.5, rightUpperArmY, rightUpperArmWidth, getImgRespHeight(images[rightUpperArm[vRightUpperArm-1]],w/15),rightUpperArmRot);    
  
  // draw chest
  context.drawImage(images[chest[vChest-1]], w*0.33+leftOffset+bmiXAdjust, y+headHeight-neckHeight-(curBreath-maxBreath-1), (w/3)+bmiWidthAdjust, chestHeight);  
  //context.drawImage(images[chest[vChest-1]], w*0.33+leftOffset, y+headHeight-neckHeight-(curBreath-maxBreath-1), w/3, chestHeight);  
  
  // DRAW VISUAL VARIABLES //
  drawImage(images[heart[heart_lvl-1]], heartXPos, heartYPos, heartWidth);  
  drawImage(images[liver[liver_lvl-1]], liverXPos, liverYPos, liverWidth);  
  
  // draw beard
  if (vBeard != 0) {
	drawImage(images[beard[vBeard-1]], skinXPos, mouthYPos-w*0.08, skinWidth*1);	  
  }  
  
  // draw mouth
  context.drawImage(images[mouth[mouth_lvl-1]], mouthXPos, mouthYPos+(mouthHeight-curMouthHeight)/2, mouthWidth,curMouthHeight);    
  
  // draw teeth overlay (brown overlay which changes teeth color)
  context.save();
  context.globalAlpha = (teeth_lvl-1)/9;
  context.drawImage(images[teethoverlay[mouth_lvl-1]], w*0.442+leftOffset, y+headHeight/1.95-curBreath+(mouthHeight-curMouthHeight)/2, mouthWidth, curMouthHeight);  
  context.restore();	      
  
  // draw wrinkles
  context.save();
  context.globalAlpha = wrinklesTransparancy[wrinkles_lvl-1];
  context.drawImage(images[wrinkles[wrinkles_img]], w*0.398+leftOffset, y+headHeight/9.5-curBreath, w/5.5, getImgRespHeight(images[wrinkles[wrinkles_img]],w/5.5));
  context.restore();   
  
  // draw eyecircles
  context.save();
  context.globalAlpha = eyecircleTransparancy[tiredness_lvl-1];
  context.drawImage(images[eyecircles[0]], eyesXPos,  y+headHeight/4.15+(maxEyeHeight-curEyeHeight)/150-curBreath, w/4.9,getImgRespHeight(images[eyecircles[0]],w/4.9)); 	 
  context.restore();     
  
  // draw eyes
  context.drawImage(images[eyes[vEyes-1]], eyesXPos, eyesYPos, eyesWidth, curEyeHeight); 	 
 
  // draw nose
  var noseWidth = w*0.035;
  drawImage(images[nose[vNose-1]], skinXPos+skinWidth/2-noseWidth/2, skinYPos+w*0.12, noseWidth);
 
  //draw hair - EXTENSION: divide hair in 2 pieces one behind the head and one in front, reduces the effort and positioning details with a cut out version. this way, hair can be used for different head types
  drawImage(images[hair[vHair-1]], w*0.277+leftOffset, y-w/7.5-curBreath, w/2.285); 	
 
  // draw left arm (with rotation)
  drawImageRot(images[leftArm[vLeftArm-1]], leftArmX+leftOffset+bmiXAdjust/1.5, leftArmY, leftArmWidth, leftArmHeight, leftArmRot);   

  // draw right arm (with rotation) // EXTENSION: replicate automatic arm placement for left hand
  drawImageRot(images[rightArm[vRightArm-1]], rightUpperArmX+(rightUpperArmHeight*rightArmRotBalance)+leftOffset-bmiXAdjust/1.5, rightUpperArmY + (rightUpperArmHeight*(1-rightArmRotBalance))+curEatRotation/10, w/14, getImgRespHeight(images[rightArm[vRightArm-1]],w/14),rightArmRot + curEatRotation);
  
  // draw accessories (age/body language);
  if (posture_lvl === 5) {
	  context.drawImage(images[walkingstick[0]], w*0.03+leftOffset+curBreath/3, leftArmY+curBreath/3+w/18, w/9,  getImgRespHeight(images[walkingstick[0]],w/9));
	  
	  // draw grandpa or grandma hat based on gender
	  drawImage(images[agehats[gender]], w*0.35+leftOffset, y-w/9.5-curBreath, w/3.5);
  }
  
  // draw eyeballs
  drawEllipse(w*0.437+leftOffset, y + headHeight/3.36+(tiredness_lvl-1)*w*0.0005+(maxEyeHeight-curEyeHeight)/8 - curBreath, w/30, w/42-(maxEyeHeight-curEyeHeight)/2, eyeColors[vEyeColor-1]); // Left Eye
  drawEllipse(w*0.549+leftOffset, y + headHeight/3.36+(tiredness_lvl-1)*w*0.0005+(maxEyeHeight-curEyeHeight)/8 - curBreath, w/30, w/42-(maxEyeHeight-curEyeHeight)/2, eyeColors[vEyeColor-1]); // Right Eye
  drawEllipse(w*0.437+leftOffset, y + headHeight/3.34+(tiredness_lvl-1)*w*0.0005+(maxEyeHeight-curEyeHeight)/8 - curBreath, w/80, curEyeHeight/6, "black"); // Left Eye Black Dot
  drawEllipse(w*0.549+leftOffset, y + headHeight/3.34+(tiredness_lvl-1)*w*0.0005+(maxEyeHeight-curEyeHeight)/8 - curBreath, w/80, curEyeHeight/6, "black"); // Right Eye Black Dot
  
  // draw glasses
  if (vGlasses != 0) {
	drawImage(images[glasses[vGlasses-1]], skinXPos+w*0.022, eyesYPos-w*0.007-(maxEyeHeight-curEyeHeight)/1.5, skinWidth*0.85);	  
  } 
  
  // draw FPS
  //context.font = "bold 12px sans-serif";
  //context.fillText("fps: " + curFPS + "/" + fps + " (" + numFramesDrawn + ")", 20, 30);
  //++numFramesDrawn;
  
  // increase redrawCounter (could be removed after first run-through)
  redrawCounter = redrawCounter + 1;	
}

// Draws transparent but clickable buttons (based on mouse click / touch coordinates)
function drawButtons(){
  
  if (redrawCounter === 1) { // check that buttons have been drawn the first time
  
	// Add clickable overlay buttons with same coordinates as the heart
	fillButtonsArray();
  }

  // Render clickable overlays
  buttons.forEach(function(button) {
		context.fillStyle = "#FFF"; 
		context.globalAlpha = 0.0;
		context.fillRect(button.left, button.top, button.width, button.height);
		context.globalAlpha = 1;
  }); 
}

// Draws an ellipse
function drawEllipse(centerX, centerY, width, height, color) {

  context.beginPath();
  
  context.moveTo(centerX, centerY - height/2);
  
  context.bezierCurveTo(
	centerX + width/2, centerY - height/2,
	centerX + width/2, centerY + height/2,
	centerX, centerY + height/2);

  context.bezierCurveTo(
	centerX - width/2, centerY + height/2,
	centerX - width/2, centerY - height/2,
	centerX, centerY - height/2);
 
  context.fillStyle = color;
  context.fill();
  context.closePath();	
}


/////////////////////////////////
//         ANIMATIONS          //
/////////////////////////////////

// Increases a counter used to delay the Last Day transition effect animation
function updateTransitionDelay() {
	curTransitionDelay += 1;
}

// BREATHING
function updateBreath() { 
				
  if (breathDirection === 1) {  // breath in
	curBreath -= breathIncrement;
	if (curBreath < -maxBreath/2) {
	  breathDirection = -1;
	}
  } else {  // breath out
	curBreath += breathIncrement;
	if(curBreath > maxBreath) {
	  breathDirection = 1;
	}
  }
}

// WAVING
function updateWaving() { 
				
  if (waveDirection === 1) {
	curWaveRot += waveIncrement;
	if (curWaveRot > maxWaveRot) {
	  waveDirection = -1;
	}
  } else {
	curWaveRot -= waveIncrement;
	if(curWaveRot < 1) {
	  waveDirection = 1;
	}
  }
}

// BLINKING
function updateBlink() { 
				
  eyeOpenTime += blinkUpdateTime;
	
  if(eyeOpenTime >= timeBetweenBlinks){
	blink();
  }
}

// BLINKING
function blink() {
  ///console.log("blink: " + curEyeHeight);
  if(tiredness_lvl <= 3){
	  curEyeHeight -= 10/tiredness_lvl;
  } else {
	  curEyeHeight -= 10/(tiredness_lvl*4);
  }
  if (curEyeHeight <= 0) {
	eyeOpenTime = 0;
	curEyeHeight = maxEyeHeight;
  } else {
	//setTimeout(blink, 30);
  }
}

// EAT
function updateEat() { 
if (eatActive === 1) {
  didntEatTime += eatUpdateTime;
	
  //when didnt eat long enough	
  if(didntEatTime >= timeBtwEat){
	  
	  // eat by moving the arm to the mouth
	  if (curEatRotation < tarEatRotation && eat===0) { // elseif if it is higher
		curEatRotation += 2;
	  } else if (curEatRotation >= tarEatRotation) {
		eat = 1;
	  } 
	  
	  // when eat, remove arm again and chew
	  if (curEatRotation > 0 && eat === 1) {
		// put arm in previous position
		curEatRotation -= 2;
		
		chewing = 1;
		// chew
		
	  } else if (curEatRotation <= 1 && eat === 1) {
		eat = 0;
		didntEatTime = 0;
		eatAssetActive = getRandomNumber(0,5);
		curMouthHeight = mouthHeight;	
		chewing = 0;
		chewTime = 0;
	  }
  }
}
}

// CHEWING
function chew(){
	if (chewTime <= 20){
		if(curMouthHeight >= mouthHeight) {
			chewDir = -5;
		} else if (curMouthHeight <= mouthHeight*0.1 ) {
			chewDir = 5;
		} 	
		chewTime++;
		curMouthHeight = curMouthHeight + chewDir;
	} else {
		chewing = 0;
		chewTime = 0;
		curMouthHeight = mouthHeight;
	}
}


////////////////////
// EVENT HANDLING //
////////////////////

// Dynamic JS definition of button position based on the position of their related objects
function fillButtonsArray() {
	buttons = [];
	buttons.push({
		width: heartWidth,
		height: heartHeight,
		top: heartYPos,
		left: heartXPos,
		name: 'heart'
	});
	
	buttons.push({
		width: liverWidth,
		height: liverHeight,
		top: liverYPos,
		left: liverXPos,
		name: 'liver'
	});	
	
	buttons.push({
		width: skinWidth,
		height: skinHeight*0.3,
		top: skinYPos+w*0.07,
		left: skinXPos,
		name: 'eyes'
	});	
	
	buttons.push({
		width: mouthWidth,
		height: mouthHeight,
		top: mouthYPos,
		left: mouthXPos,
		name: 'mouth'
	});	
	
	buttons.push({
		width: w*0.9,
		height: w*0.15,
		top: topSection+avatarSection,
		left: leftOffset+w*0.05,
		name: 'btnBottom01'
	});
	
	buttons.push({
		width: messageButtonWidth,
		height: messageButtonHeight,
		top: messageButtonY,
		left: messageButtonX,
		name: 'msgBtn'
	});	
	
	buttons.push({
		width: lastDayOverviewWidth,
		height: replayButtonHeight*1.2,
		top: replayButtonY,
		left: lastDayOverviewX,
		name: 'lastdayreplay'
	});		
}


/////////////////////////////////
//  DETAILS ON DEMAND FEATURE  //
/////////////////////////////////
// Handles the logic for popup detail on demands when clicking on the avatar

// Sets a variable to 1 which will be checked on redraw() resulting in the popup being drawn
function openDoD(variable) {
	variable[1] = 1;
}

// Sets all dod popup variables to 0 to hide all of them (during redraw())
function closeAllDoD() {
	showDoD.forEach(function(entry) {
		entry[1] = 0;
	});
}


//////////////////////////
// VARIABLE CALCULATION //
//////////////////////////

function calculateBodyHeight(){
  chestHeight = getImgRespHeight(images[chest[vChest-1]],w/3);
  headHeight = getImgRespHeight(images[head[vHead-1]],w/3.5);
  upperBodyHeight = chestHeight+headHeight;

  hipHeight = upperBodyHeight*0.3// getImgRespHeight(images[hip[vHip-1]],w/3);  
  legHeight = getImgRespHeight(images[rightLeg[vRightLeg-1]],w/9);
  lowerBodyHeight = hipHeight + legHeight;

  upperArmHeight = getImgRespHeight(images[leftUpperArm[vLeftUpperArm-1]],w/15);
  neckHeight = w/12;
  
  bodyHeight = upperBodyHeight + lowerBodyHeight;
}

function getImgRespHeight(image, width) { //calculates w/3*images[hip[vHip-1]].height/images[hip[vHip-1]].width
	return width*image.height/image.width;
}


/////////////////////////////////
//      GENERAL FEATURES       //
/////////////////////////////////

// TODO: Delete after project is finished
//function updateFPS() { 
//	
//	curFPS = numFramesDrawn;
//	numFramesDrawn = 0;
//}

// Shows error messages based on their type
function showError(error) {
	switch (error) {
		case "noserver":
			alert("Es kann keine Verbindung zum Server hergestellt werden kann. Versuchen Sie es später wieder.");
			break;
			
		case "data":
			alert("Avatardaten können nicht geladen werden. Bitte beachten Sie, dass dieser erst nach 4 Tagesprotokollen zur Verfügung steht.");
			break;
			
		case "nointernet":
			alert("Der Avatar kann nicht abgerufen werden, da keine Verbindung zum Internet besteht.");
			break;
			
		default:
			alert("Ein unbekannter Fehler ist aufgetaucht. Bitte melden Sie sich bei da.meusburger@gmail.com")
	}
}

// Event handling logic
function checkButtonsClicked(x,y){
	
		var clickedOnDoD = 0;
		buttons.forEach(function(button) { // if clicked on an button
			if (y > button.top && y < button.top + button.height && x > button.left && x < button.left + button.width) {
				switch (button.name) {
					case "btnBottom01":
						if (tutorialActive === 1) {
							tutorialStep += 1;					
						}
						eyesNotUpdated = 1;
						break;
						
					case "msgBtn":
						if (messageActive === 1) {
							messageActive = 0;
						}
						break;	
						
					case "heart": 
						clickedOnDoD = 1;
						if(heartDoD[1]===0) { // if details on demand window is not open
							closeAllDoD();
							openDoD(heartDoD); // show details on demand by setting the value to 1
						} else {
							closeAllDoD();
						}
						break;

					case "liver":
						clickedOnDoD = 1;
						if(liverDoD[1]===0) { // if details on demand window is not open
							closeAllDoD();
							openDoD(liverDoD); // show details on demand by setting the value to 1
						} else {
							closeAllDoD();
						}						
						break;
						
					case "eyes": // show details on demand by setting the value to 1;
						clickedOnDoD = 1;
						if(eyesDoD[1]===0) { // if details on demand window is not open
							closeAllDoD();
							openDoD(eyesDoD); 
						} else {
							closeAllDoD();
						}				
						break;	
						
					case "mouth": // show details on demand by setting the value to 1;
						clickedOnDoD = 1;
						if(mouthDoD[1]===0) { // if details on demand window is not open
							closeAllDoD();
							openDoD(mouthDoD);
							openDoD(teethDoD); // show details on demand by setting the value to 1
						} else {
							closeAllDoD();
						}				
						break;
						
					case "lastdayreplay": // replay last day animation if it exists
						if (transitionDone === 1) {
							// update the avatar to show the old data
							updateAllVisualVariables("old"); // ensure that all visual variables are updated to the old values	
							
							// reactivate the animation
							transitionDone = 0;
							transitionActive = 1;
							ingredientInAnimation = 0;
							curTransitionDelay = 0;
							eatActive = 0;
						}
						break;
						
					default:
				}
			}
		});
		
		//if clicked but not on any DoD
		if (clickedOnDoD === 0) {
			closeAllDoD();
		}	
}

// Returns random rounded number from min (included) to max (not included)
function getRandomNumber(min, max) {
    return Math.floor(Math.random() * (max - min) + min);
}

