# Quality Control of Crowd Labeling
This repository is created for Quality Control of Crowd Labeling Project under Professor Edward Gehringer. 

## Abstract
Peer-assessment-based educational methods are becoming more widespread. These methods involve students reviewing projects and comments created by their peers and providing suggestions for improvement. However, the effectiveness of this process depends on the quality of the comments in the reviews. We have devised natural-language processing approaches to evaluate review comments based on machine learning. The accuracy of these approaches depends on the quality of the training data.  Our training data consists of comments labeled by students as containing or not containing certain characteristics, such as suggestions or explanations.  This paper reports on our strategies for automatically vetting labels (“tags”) assigned by students.

But can we validate the quality of student tagging?  To measure the quality of individual tags, as well as the reliability of the student taggers, several strategies have been implemented. The first strategy attempts to identify students who tag “too fast,” and assign tags so quickly that they could not have given them adequate consideration.  Another approach is to exclude tags where different students disagree on whether the comment should or should not have been tagged.  A third metric looks for “anti-patterns,” such as all tags set to yes, all tags set to no, alternating yes and no, or repeated sequences such as “yes, yes, no, yes, yes, no, yes, yes, no.”  The final approach is “labeler calibration,” where tags assigned by a student are compared with tags that would be predicted from the training data that we have previously collected. This research aims to assign reliability metrics to each tag and tagger, and provide these metrics to researchers, who will be able to derive machine-learning training datasets by filtering the tags to create datasets with only the most reliably tagged data, or larger datasets that also include less-reliable tags.

## Database Tables used:
Link to all the Tables in the Database: [Documentation on Database Tables](https://expertiza.csc.ncsu.edu/index.php/Documentation_on_Database_Tables)
<br><br>
Tables Used:
1. [Answer tags](https://expertiza.csc.ncsu.edu/index.php?title=Answer_tags)
![Alt text](https://imgur.com/dAPeTKZ)
2. [Answers](https://expertiza.csc.ncsu.edu/index.php?title=Answers)
3. [Tag prompt deployments](https://expertiza.csc.ncsu.edu/index.php?title=Tag_prompt_deployments)
4. [Teams Users](https://expertiza.csc.ncsu.edu/index.php?title=Teams_users)
5. [Submission records](https://expertiza.csc.ncsu.edu/index.php?title=Submission_records)
