# Group logbook

## First team meeting: 5. 9.2025 (during the first introduction seminar)
**Present:** All (Nette, Janna, Emma, Yuhan, Ville and Matej)


**What was discussed/decided:**
- Got to know eachother
- Telegram the main communication channel (created a chat group)
- We will use github (& created a repository)
- We’ll read the project instructions again (more closely) and think about what should we do and how
- Email prof. and the client

- Next meeting will be on tuesday 9. 9. 16.00 online:
  - Everyone will read the project instruction, think about the project and what we are going to ask from the client and Jussi 

## Second team meeting: 9. 9.2025 (online)
**Present:** All (Nette, Janna, Emma, Yuhan, Ville and Matej)
**What was discussed/decided:**
- We did some research on the problem and have some idea about the workflow
- We will contact the client today
- GitHub discussions could be nice place for communicating on abstract problems that do not require issue on github

## Wednesday 17.9 
## Online meeting before client meeting 13:15–13:45
- We briefly went through what we want to ask in the client meeting about the project
- We agreed that everyone can ask questions
  - The assumption is that the meeting will be relaxed and informal, where we will discuss the project in more detail, receive clearer instructions/information about the project goals and implementation and have the chance to ask clarifying questions
## Client meeting 14-14:30
- We received clarification from the client during the meeting about the project goals and guidelines which was our main objective.
   - The most important task is finding the ditches and then categorizing them into new & old ones and by their condition
- The outcome could, for example, be a QGIS plugin or another open environment
  - The project is very open-ended and as it progresses we can see what we are able to achieve and what the best implementation method will be
- AI is not necessarily required in this project

- The meeting was educational and somewhat different from what we had initially expected when preparing for it
  - We realized that we could have gathered information more effectively if we had thought more carefully in advance about the key questions and the structure of the meeting
  - --> Next time, we will prepare more thoroughly and ensure that everyone has a clear role in the meeting so that we can make the most of it

- In the end the outcome was clear: we need to obtain the data so that we can move forward to start finding the ditches.

## Friday 19.8, 9:30–11:00 at campus
**Present:** Nette, Emma, Ville, Matej
Place: Campus

**Summary of the meeting:**
- Reflected on the last meeting and the project so far
- Discussed the project timeline:
   - Meeting more, both short online meetings to catch up and also in person meetings at campus

Some roles assigned:
- Responsible for logbook: Nette (others will add contributions if needed)
- Responsible for sending emails: Matej

- Discussed the data, the basic steps of machine learning, training data and how to use it to detect ditches.
- Planned to start experimenting in pairs, trying out different methods and then reviewing together what worked and what didn’t.

Before next time (learning tasks):
- Study a bit about:
  - U-Net, Random Forest, (Traditional models), as possible test cases
  - There are some articles about U-Net and related papers in the GitHub repository.

Review basics of machine learning:
- Difference between training, validation, and testing
- Neural networks and convolutional networks

**Next meetings:**

**Monday 10:00 – online**

**Thursday 9:00 – in person at campus**

At the next meetings we’ll:
- Agree more precisely on roles
- Decide on three articles/methods to start testing (a total of three different ones at first).
- Get started!!




What we should learn:
U-network, papers in the github
Basics about machine learning, basic idea
Difference between training, validation, testing
Neural networks, convolutional networks
-	Then u-network
Random forest


## Monday 22.9 (online meeting)
Present: all

- Quick catch-up on where we are and what needs to be done before Thursday’s in-person meeting:

  - We will reach out again regarding the data and try to figure out how we can access it before Thursday (cloud / hard drive, etc.)

  - We discussed preliminarily how to do the preprocessing (Python / TerraScan or similar) to obtain the DTM (ground surface)

  - Data split: training / validation / test

- We selected two different methods: U-Net and Random Forest

- We divided into groups:

  - U-Net: Matej, Ville and Yuhan

  - Random Forest: Nette, Janna and Emma

- Each group will explore their method in more detail and how to apply it in this context before Thursday

**- Next meeting:**
**Thursday 25.9, 9:00 at campus**

- Data review, preprocessing planning/start and agreeing on next steps

## Thursday 25.9
9:00–11:30 , At campus

Present: all

- Started by reviewing the data together

- Opened part of the laser scanning data in Terrascan in order to create the DEM model

  - Already filtered → directly obtained the ground layer

  - Done using Terrascan

- Started data preprocessing:

  - Editing laser scanning data (DEM model) and selecting the area for initial testing

  - Adjusting validation data to fit the point cloud data (continuing later)

  - Editing ditch data: creating buffers for ditches and rasterizing (continuing later)

Next: meeting in small groups
  - Starting to try the methods 

**Next meeting together: online on Friday 10:00**
 
## Friday 3.10 
Online Meeting (10:00–10:20)

Present: Nette, Emma, Ville, Matej, Yuhan

- Catch-up:

  - Reviewed what we have worked on in small groups

  - Discussed questions that came up regarding datasets and methods

  - Discussed about some codes developed so far, what can be utilized in both cases and clarified the explanations

- Next meeting:

  - Tuesday 7.10 9:00 (online)

  - Go through in more detail where we currently stand and what results have been obtained

  - Assign roles for the client meeting and prepare more thoroughly for its flow

- Client meeting: Wednesday 14:00 (online)

## Tuesday 7.10
Online meeting (9:00-9:45)

Present: Nette, Emma, Janna, Matej

- Reviewed progress in both projects
- Both groups seem to be in a good phase, no major dead ends identified
- Agreed on division of tasks for tomorrow’s client meeting:
   - Both groups will briefly present their workflow, current progress and raise any questions
   - Order of presentations: Random Forest first, then U-Net
     - Shared PowerPoint presentation will be used
     - At the end: mention observations on inaccuracies in the validation data
  - Questions to clarify with client:
      - Validation data – accuracy concerns
      - Preferred format for the final output data? (so that code can be built accordingly)

- Task division for client meeting:
    - Meeting lead: Nette
    - Notes: Janna
    - Workflow presentation & progress:
        - Random Forest: Emma
        - U-Net: Matej?
- Proposal: schedule another meeting in about three weeks (29.10?)

## Wednesday 8.10 second client meeting 
Online meeting (14-14:30)

Present: All

- Both groups prestened what they have done so far

Random Forest

- Nette presented the Random Forest workflow and also led the meeting
  - The approach was tested with a small study area (1 km^) where 25% was for testing and 75% for training
  - The workflow is mainly based on study https://www.sciencedirect.com/science/article/pii/S0957417422003876
    
- Emma presented the results 
  - The model achieved moderate performance in ditch detection
  - The major challenge is still that the model detects a notable number of false positives (68%)
  - Results suggest that further feature refinement and training data improvments are needed for higher accuracy
  - In addition, more training data and test data is needed
 
- Next steps in Random Forest
  - Apply post processing to refine predictions
  - Train and test tehe model using larger study area.
  - Considering the age and condition of ditches

U-net

- Ville presented the U-Net approach
  -  The workflow is mainly based on study https://doi.org/10.1080/20964471.2025.2491177
 
- Next steps in U-net
  - Test pre-trained model​
  - Fine tune pre-trained model​
  - Train model from scratch​
  - Compare/Evaluate

Plugin development 

-  Matej presented the uppcoming steps in plugin development
  - Which type of data the client would like as input for the plugin
  - LiDAR (.laz) or Digital Elevation Model (DEM)


Some extra notes:
- Next meeting on friday 17.10 (online)
- We are waiting to get access to the CSC supercomputer so we can test the models with a larger dataset.
- The client was satisfied with our results, and the purpose of this meeting was mainly to present our current progress.



## Friday 17.10
Online meeting (9:15-9:45)

Present: All

- Both groups have made progress on their projects
- How can we obtain a larger dataset to use as the base DEM model?
    - Matej will preprocess the entire dataset and share it with both groups
- Who will participate in the computing session on Friday, Oct 24?
  → Access for Ville, Emma and Janna (others can join as well)
- Ville will reply to Bryan’s message.
- Are the ditches next to roads considered actual ditches or not? → To be clarified and asked from the client

- Mid-seminar next Wednesday (Oct 22):
    - Update the previous client meeting slides with current progress
    - Add a short introduction about the project’s goals, target outcomes and clearly define the next steps
    - Both groups will update their respective parts of the slides
    - To-do:
      - Introduction (Janna)
      - Next steps

- Next meeting:
  - Tuesday at 9:15 (online)
  - The mid-seminar material should be ready by then and we’ll finalize the presentation structure and details

## Tuesday 21.10
Online meeting (9:15-10:10)

Present: All

- Reviewed tomorrow’s mid-seminar presentation and discussed the current results and related reflections
- Decided how to divide the presentation and who will present each part
  - Presentation slides can be found in the OneDrive Project Course 2025 folder
- Reviewed the input data (DEM) and discussed how and in what format it can be integrated into the project
  - The Random Forest group will check how to include the full dataset prepared by Matej into their own work.

- On Friday there is a computing session
  - Will clarify if any code modifications are needed or if the environment needs to be changed
 
- We did the mid-term assignment
  - Wrote down during the meeting by Nette and shared with the rest of the group for editing
 
- **Tomorrow: Mid-term seminar 9:00–13:00**
  - After the seminar we’ll agree on the next meetings in more detail

- Friday computing session at 11:00.

## Friday 24.10
Online meeting (11-11:30)
Present: Ville, Janna, Nette, Emma, Yuhan

- We went through the CSC platform and how it works and we received useful links to resources and other helpful tips
- Based on that we will continue with the model training and will reach out if we encounter any issues
  - Janna (Random Forest) and Ville (U-Net) will test the model training.

- Next group meeting on Monday where we will:
  - Go through the results
  - Prepare for the client meeting
  - Define a clear workflow for the next steps
  - Divide the group to focus on different parts:
    - Age
    - Condition
    - GIS plugin

## Monday 27.10
Online meeting (16-17)
Present: Nette, Emma, Janna, Ville, Matej

- Project update
  - Reviewed the progress of model training
  - Some challenges adapting the code to the CSC environment but work is progressing

- Client Meeting on Wednesday
  -  Agenda:
    -  Model results
    -  Workflow for age and condition estimation
    -  Challenges encountered (e.g., data quality issues)
    -  What kind of documentation does the client want?

- Next stpes:
  - Continue training and refinement of the models
  - Finalizing model training → evaluating results
  - Estimating ditch age (based on vegetation, aerial imagery and ditch geometry etc)
  - Assessing ditch condition
  - Designing the QGIS plugin
 
- Additionally:
  - Planning to use Street View/time-series analysis etc to further evaluate model performance
    - to understand what causes false positives/negatives
    - what factors explain the model’s behavior
    - what leads to erroneous predictions

- Next meeting:
  - Client meeting, Wednesday 29.10 klo 14 -> (online)
  - Next group meeting will be desided later on


## Wednesday 29.10 Client meeting
- Ville presented the U-Net approach
  - Ville had previously sent a map showing the current results
  - Discussion on whether the errors were false positives or actual ditches
    
- Janna presented the Random Forest approach
  - Still problems with the larger dataset
  - Possible decision to choose U-Net since it performs better
  - Need to decide whether to continue with Random Forest as well
    
- Nette presented the initial workflow for age determination
  - Problems with age detection: tree cover affects results 
  - Soil type has a strong influence
    
- Matej presented theworkflow with QGIS plugin
  - QGIS Python does not have ML libraries
  - Proposed solution with two components:
    - QGIS plugin – UI integration
    - Docker environment – ML backend
      
**Documentation and outcomes**
  - The client will discuss with the Forest Centre what kind of documentation and outcome they need and will send an email about this next week
- Other wishes for the plugin:
  - Easy to use
- Tips for age analysis:
  - The client will consider if they can help us and inform later
  - Things to consider: It is possible to calculate vegetation indices also from aerial images; the green band may be needed
    - The client provided a link to pre-calculated vegetation indices
 - The results do not necessarily have to be highly accurate, rough time estimate is enough
 - The client understands thath this is a hard task and the main point is that we have tried different approaches and understood the process
   and in the documentation, it is important to describe what we have done and found so they can continue our work

- U-Net model discussion
  - The client asked how the 0.8 probability threshold was chosen
  - Ville explained he simply tested different values and found 0.8 looked better than 0.5, without a scientific basis
  - The client noted that 0.8 removes too many ditches, based on their own comparison
  - Suggestion: add a feature to the plugin allowing the user to set their own probability threshold
  - Some new ditches were found that are not visible on the base map and the client was pleased with this

- Next steps
  - The client commented that overall the results look very good
  - The group will continue their work with improving ditch detection, age classification and QGis plugin
  - Client will sent info about documentation and possible tips
  - **Next and final meeting on 19.11. 14:00 on Teams**

## Tuesday 4.11
Online meeting (9:15-9:45)

Present: All

- We now have results from both models and we went through the results
  - The U-Net model performs better --> we will continue with that
  - We are currently waiting for a response from the client regarding whether we should proceed with the model trained using Hytky label data or with the more accurate model based on the Swedish study data
  - Ville is working on the model (implementing necessary changes to integrate it into the plugin)
- Age determination:
  - Nette, Emma & Janna
  - Comparing old vs. new laser scanning data (DEM) with time intervals of 5 and 10 years
  - User of the model provides the DEMs
  - The model compares new and old datasets and creates layers based on those observations
  - Also exploring possibilities to utilize aerial images

- Plugin:
  - Matej and Yuhan are working on it

- Next week we will also start preparing the documentation and the poster
- Next meeting: Tuesday, 11.11 at 9:15 (online)

## Tuesday 11.11
Online meeting (9:15-9:50)

Present:  Nette, Emma, Janna, Yuhan, Matej

- U-net model for detecting ditches is almost ready and has been modified according to the client’s wishes (producing probability, depth and binary maps)
- Plugin is a work in progress, still needs all methods to be finalized before it can be built
- Age determination works but some testing of thresholds and buffer sizes is still ongoing
  - The goal is to finish the code within the next few days so it can be integrated into the plugin as soon as possible

- Documentation and poster:
  - Deadline for materials (poster at least ready): 24.11
  - Also the group logbook deadline: 24.11
  - (Learning diary deadline: 21.11)

- Task division:
  - Yuhan takes the lead on the poster
  - Ville starts working on the model documentation and others add the necessary points
  - Everyone continue working on unfinished tasks
  
- Aim to have everything working this week so next week can focus on final polishing

- Next meeting:
- In-person at campus on Tuesday 18.11 at 9:15
  - Go through everything together to make sure all is okay
  - Prepare the final presentation for the client meeting on Wednesday 19.11 at 14:00->
  - Work on the poster/divide poster sections
  - Assign and agree on all finalization tasks (who handles what etc.)

  ## Tuesday 18.11
  Meeting at campus (9:15-10:45)
  
  Present: All

  - Reviewed the trained model and the GUI interface: what it looks like and how it works
  - Discussed age determination results; went through outputs and everything works well
    - Modifiding codes to work with the GUI interface and ensured it can also be executed via command line so it can be integrated into the GUI
  - Created the presentation outline for tomorrow’s final client meeting and divided tasks:
    - Nette: introduction, age determination, conclusion
    - Matje: output, GUI results
    - Emma: age determination
    - Janna: documentation and report
    - Yuhan: takes notes

  - Nette and Janna begin writing the report; others will add detailed descriptions of their own workflow steps
  - Poster is almost ready; final output still needs to be added and corrected before next Monday
  - Age determination feature has been included in the GUI
  - Learning diaries must be submitted by Friday
  - Next week, we will review the final seminar presentation and the poster presentation
  - Otherwise, everything is nearly ready!
    
  - Next:
    - Client meeting tomorrow, 19.11 (online)

## Wednesday 19.11 Final Client Meeting
Online meeting (14:00–14:30)

Present: All

**What was presented:**
- Introduction: The complete workflow and outcomes of the project.
- GUI Application:
  - Matej demonstrated the standalone PySide6 GUI.
  - Explained why we shifted from the QGIS plugin to a standalone GUI (library conflicts with QGIS Python environment).
  - Inference is working perfectly. Training and Testing tabs will be finalized before next Monday.
  - Feedback: The client said they liked the standalone GUI more than the QGIS plugin.
- Age Determination:
  - Nette presented detecting new ditches by comparing probability maps from different years.
  - Emma presented using National Land Survey (NLS) vector data (2005–2025) to identify when ditches first appeared.
  - Feedback: Clients acknowledged that age verification is very hard but considered our approach a very good baseline for the future.
- Report:
  - Janna presented the final report structure.
  - Feedback: Clients were satisfied with the proposed structure. They mentioned they had no immediate additions but might have some questions later.

**Discussion**
- The clients asked if the model can handle the  20 points/m² laser data.
  We believe the model should work, as the difference between 5 pts and 20 pts is not as big as between 0.5 pts and 5 pts. However, it needs testing first. 

**Next:**
- Finalize the GUI (implement the training/testing logic connections).
- Submit the final report, user documentation, poster, and all code materials to the clients and the school by next Monday.



