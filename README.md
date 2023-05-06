# Quality Control of Crowd Labeling
This repository is created for Quality Control of Crowd Labeling Project under Professor Edward Gehringer. 

## Abstract
Peer-assessment-based educational methods are becoming more widespread. These methods involve students reviewing projects and comments created by their peers and providing suggestions for improvement. However, the effectiveness of this process depends on the quality of the comments in the reviews. We have devised natural-language processing approaches to evaluate review comments based on machine learning. The accuracy of these approaches depends on the quality of the training data.  Our training data consists of comments labeled by students as containing or not containing certain characteristics, such as suggestions or explanations.  This paper reports on our strategies for automatically vetting labels (“tags”) assigned by students.

But can we validate the quality of student tagging?  To measure the quality of individual tags, as well as the reliability of the student taggers, several strategies have been implemented. The first strategy attempts to identify students who tag “too fast,” and assign tags so quickly that they could not have given them adequate consideration.  Another approach is to exclude tags where different students disagree on whether the comment should or should not have been tagged.  A third metric looks for “anti-patterns,” such as all tags set to yes, all tags set to no, alternating yes and no, or repeated sequences such as “yes, yes, no, yes, yes, no, yes, yes, no.”  The final approach is “labeler calibration,” where tags assigned by a student are compared with tags that would be predicted from the training data that we have previously collected. This research aims to assign reliability metrics to each tag and tagger, and provide these metrics to researchers, who will be able to derive machine-learning training datasets by filtering the tags to create datasets with only the most reliably tagged data, or larger datasets that also include less-reliable tags.

## Database Tables used:
Link to all the Tables in the Database: [Documentation on Database Tables](https://expertiza.csc.ncsu.edu/index.php/Documentation_on_Database_Tables)
<br>
<img src="https://i.imgur.com/BRIY6cj.png" alt= “” width="500" height="500">
<br>
Tables Used:
1. [Answer tags](https://expertiza.csc.ncsu.edu/index.php?title=Answer_tags)<img src="https://i.imgur.com/dAPeTKZ.png" alt= “” width="600" height="500">
2. [Answers](https://expertiza.csc.ncsu.edu/index.php?title=Answers) <img src="https://i.imgur.com/aM3iRG8.png" alt= “” width="600" height="500">
3. [Tag prompt deployments](https://expertiza.csc.ncsu.edu/index.php?title=Tag_prompt_deployments) <img src="https://i.imgur.com/xrVrgsU.png" alt= “” width="600" height="500">
4. [Teams Users](https://expertiza.csc.ncsu.edu/index.php?title=Teams_users) <img src="https://i.imgur.com/vjBEOMp.png" alt= “” width="600" height="500">
5. [Submission records](https://expertiza.csc.ncsu.edu/index.php?title=Submission_records) <img src="https://i.imgur.com/sWLuIi3.png" alt= “” width="600" height="500">


## Results: 
1. Fast Tagging values of each tagger 
<img src="https://i.imgur.com/j8VgE5k.png" alt= “” width="600" height="500">
<br>
The resulting table includes assignment_id, user_id present in that assignment, and the fast tagging logarithmic timestamp value of each user. This table provides researchers with a quick and easy way to evaluate the speed and efficiency of their annotators and identify potential quality issues. Researchers can compare the average tagging time of each student with a pre-defined threshold to determine whether they are tagging too quickly or too slowly.

The resulting table from the fast tagging strategy is a powerful tool for researchers to evaluate the efficiency and quality of their annotators. By including the assignment_id, user_id, and fast tagging logarithmic timestamp value of each user, the table provides a clear and comprehensive overview of the tagging process.

Researchers can use the table to quickly identify any potential quality issues and to compare the efficiency of different annotators. By comparing the average tagging time of each student with a pre-defined threshold, researchers can easily determine whether an annotator is tagging too quickly or too slowly. This can help to identify potential quality issues, such as inadequate training or insufficient time spent reviewing the data, and take corrective action to improve the quality of the assigned labels.

2. Krippendorff's alpha coefficients for each tagger 
<img src="https://i.imgur.com/dyX1Yo3.png" alt= “” width="600" height="500">
<br> 
We output a table showing the assignment ID, team ID, user ID, and Krippendorff's alpha values of each user. This table can be used by researchers to classify users as reliable or not based on the Krippendorff's alpha values. Our results suggest that researchers can use this table to identify reliable team members and exclude unreliable ones, thereby improving the quality of the labeling process.

Our results included negative, positive, and zero values for Krippendorff's alpha. These values were indicative of the level of agreement or disagreement among team members. Negative values indicated that the user was in disagreement with their teammates, and positive values indicated that the user was in agreement with their teammates. Zero values indicated that there was no level of agreement or disagreement.

Our results showed some NaN values for cases where we cannot calculate Krippendorff's alpha values for particular users. These cases included situations where there was just one person in the team or when all the students gave the same tag values to all the tags, and hence there was no other value to consider. These NaN values were excluded from our analysis.


3. Pattern Detection for each tagger 
<img src="https://i.imgur.com/DVqij0u.png" alt= “” width="600" height="500">
<br>
Our results provide a detailed table that includes assignment_id, user_id, pattern found or not, the specific pattern that was identified, and the number of repetitions for each pattern. This information enables researchers to identify unreliable workers who are following a pattern and classify them accordingly.

By providing this table to researchers, we can help them to make informed decisions about which workers to include in their dataset and which to exclude. This can lead to better-quality data and more accurate predictions from machine learning models.

We found that the table provided by our algorithm was easy to interpret and understand, making it accessible to researchers of all levels of technical expertise. This makes our algorithm an ideal tool for crowd labeling quality control in a wide range of settings.

The table also provides researchers with insights into the specific patterns that workers are following, enabling them to identify potential sources of bias in their data. By addressing these biases, researchers can improve the accuracy and reliability of their data, leading to better outcomes and more informed decisions.


4. IRR values for each tag
<img src="https://i.imgur.com/zddt5sm.png" alt= “” width="600" height="500">
<br>
To further understand the patterns in the data, we included assignment_id, team_id, answer_id, tag_prompt_id, tag_value, and fraction in the table we provided. The assignment_id refers to the unique identifier for the task assigned to the crowd workers. The team_id refers to the unique identifier for the group of crowd workers who worked on the same task. The answer_id refers to the unique identifier for each response given to the crowd worker's work. The tag_prompt_id refers to the unique identifier for each tag prompt given to the crowd workers. The tag_value refers to the crowd worker's assigned value for each tag prompt, which can be either 1 or -1. Finally, the fraction refers to the proportion of the team that agrees with the assigned tag value.

By including this additional information in the table, researchers can gain deeper insights into the reliability of the tags assigned by the crowd workers. They can use this information to make more informed decisions about which tags to trust and which tags to discard. For example, tags with high IRR values and fractions close to 1 can be considered highly reliable, while tags with low IRR values and fractions close to 0.5 may need to be re-evaluated.


