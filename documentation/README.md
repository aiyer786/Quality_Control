# Code Base Explanation

## Table of Contents

**1.** [Assembly.PY](#assemblypy)

**2.** [MySQL.py](#mysqlpy)

**3.** [TaggerClassifier.py](#taggerclassifierpy)

**4.** [TagClassifier.py](#tagclassifierpy) 

**5.** [PatternDetection.py (Refactored)](#patterndetectionpy-refactored)

**6.** [Generated CSV Files](#generated-csv-files)

<br>

## Assembly.py

The `assembly.py` file serves as the master file for the application, housing wrapper functions for various features. The core logic for each feature resides in separate files, including `TaggerClassifier`, `PatternDetection_refactored`, `MySQL`, and `TagClassifier`. Additionally, users have the flexibility to provide arguments such as Minimum Log Time, Minimum Value of Alpha, Minimum Pattern Length, Minimum Pattern Repetition, and Maximum Pattern Length while executing the file.
<br><br>
### GetIntervalLogs Function

- The `GetIntervalLogs` function begins by establishing a hashmap indexed by assignment ID and user ID, utilizing a provided list of tags. It proceeds to compute interval logs for each value using the methodology outlined in the `TaggerClassifier` file. The resulting table is then saved into a file named `Interval_logs.csv`.
<br><br>
### getUserHistory Function

- Within the `getUserHistory` function, credibility scores are computed for a given list of tags. The calculation leverages the algorithms from the `TaggerClassifier` file. Following score computation, the function cleanses HTML tags from the output and records the credibility scores into a file named `userdata.csv`.
<br><br>
### getKrippendorfAlpha Function

- This function is tasked with obtaining the Krippendorf Alpha value for each user. Initially, it aggregates all tag prompt IDs for the answers of a team. Subsequently, for each tag prompt ID, it collects the raters' data. This data is then passed to the `KrippendorfAlpha` function within the `TaggerClassifier`. The resulting output is written to a CSV file.
<br><br>
### getPatternResults Function

- Utilizing a provided list of tags, `getPatternResults` function populates a user-assignment hashmap. Subsequently, it delegates this data to the `patternDetectionResult` function within the `PatternDetection` file. The outcomes are written to a file named `Patternrecognition.txt`.
<br><br>
### CalculateCredibility Function

- This function calculates credibility scores by averaging normalized log time, alpha, and total characters.
<br><br>
### CombineCSVResults Function

- The `CombineCSVResults` function consolidates all CSV and TXT files into a single file based on assignment ID and UserID. It addresses edge cases, such as those with no patterns, and computes credibility scores using the `CalculateCredibility` function.
<br><br><br>
## MySQL.py

This file facilitates connection to a MySQL database, where a dump file is currently utilized to operate the database. Once connected, the file provides helper functions for interacting with the database.
<br><br>
### getAnswerTags Function

- This function executes an inner join operation on `AnswerTags` and `TagPromptDeployments`, returning a list of `AnswerTags` with associated `AssignmentID`.
<br><br>
### getUserTeams Function

- `getUserTeams` retrieves all tags for a specific team across all assignments from the database. It organizes the data into a dictionary format: `{assignment_id: {team_id: {user_id: {answer_id: {tag_prompt_id: tag}}}}}`.
<br><br><br>
## TaggerClassifier.py

This component categorizes tags as either reliable or unreliable, employing various algorithms and metrics.
<br><br>
### BuildIntervalLogs Function

- `BuildIntervalLogs` computes the logarithm base 2 of time differences between two consecutive tags and returns the average of the result.
<br><br>
### intervalLogsforTags Function

- Within this function, interval log values are computed from a list of tags.
<br><br>
### compute_Krippendorff_Alpha Function

- Utilizing the Krippendorf alpha library, this function calculates the alpha value based on a 2-dimensional array of raters and tag prompts. The calculation is omitted if there is insufficient variation.
<br><br>
### CalculateTagCredibilityScore Function

- By integrating fast-tagging values and Krippendorff Alpha, credibility scores are generated for each tag ID. The score is determined by averaging normalized alpha and interval logs.
<br><br><br>
## TagClassifier.py

- This file contains a function to calculate agreement/disagreement amongst peers.

- We provide the function `calculateAgreementDisagreement` with a 2D array of raters and `tagpromptID`.

- For each iteration of the 2D array, we get a new `tagpromptID`, and we determine the most common rating for that ID. It then calculates the fraction of users who agree with the common rating and who don’t. The values are returned by the function in the form of a dictionary.
<br><br><br>
## PatternDetection.py (Refactored)

This Python code defines a class called `PatternDetection`, which contains methods for detecting patterns in binary data. Here is an explanation of each part of the code:
<br><br>
### PlaceHolderNode Class

- This is a nested class within `PatternDetection`.
- It's used as a custom data structure to store information about positions (LP and SP).
<br><br>
### CheckPattern Method

- This method checks for a specific pattern within a given interval.
- It takes the starting index (`lptr`), ending index (`rptr`), pattern length (`period`), and binary data (`bin_data`) as input parameters.
- It returns a list containing a boolean indicating if a pattern is found, the pattern itself, and the number of repetitions.
<br><br>
### PeriodicityCheck Method

- This method performs periodicity check and validation on the binary data for a given period.
- It takes binary data (`bin_data`), pattern length (`period`), and minimum number of repetitions (`min_tags`) as input parameters.
- It uses a custom data structure (`PlaceHolderNode`) to keep track of LP (last position) and SP (start position) for each position in the period.
- It iterates through the data and updates LP and SP based on certain conditions.
- It calls the `CheckPattern` method to check for patterns within the specified intervals.
- Returns a list containing a boolean indicating if a pattern is found, the pattern itself, and the number of repetitions.
<br><br>
### PTV Method

- Stands for Pattern Time Variation.
- It sorts a list of tags based on their creation time and converts them into binary data.
- It iterates through different pattern lengths (`Lmin` to `Lmax`) and calls the `PeriodicityCheckAllPatterns` method for each length.
- Returns a list of patterns found with their counts.
<br><br>
### PeriodicityCheckAllPatterns Method

- Similar to `PeriodicityCheck`, but it iterates through all patterns within a given period.
- It calls the `CheckPattern` method for each pattern and accumulates the results.
- Returns a list of patterns found with their counts.
<br><br><br>
## Generated CSV Files

1. **Interval_logs.csv:**
   - Column Names: Assignment_id, User_id, IL_result, Time, Number_of_Tags

2. **Krippendorff.csv:**
   - Column Names: Assignment_id, Team_id, User_id, Alphas

3. **User_data.csv:**
   - Column Names: User_id, Assignment_id, Question, Score, Review_Comment, Tag_Prompt, Tag_Value, Credibility_Score

4. **Answers.csv:**
   - Column Names: id, question_id, answer, comments, response_id
