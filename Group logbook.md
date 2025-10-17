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
Online meeting 14-14:30


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
