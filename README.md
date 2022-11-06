# COMP1828 - Advanced Algorithms and Data Structures | Coursework | University Of Greenwich

## Table of Contents:
| Section | Description |
| --- | --- |
| [Introduction](#introduction) | An introduction to the project. |
| [Task](#task) | The tasks that this coursework has for us to complete. |
| [Code glossary](#code-glossary) | A glossary of the various bits of code I have written for this project. |
| [References](#references) | The references I have used for this project. |
| [Author and license](#author-and-license) | The author and license of this project. |

## Introduction:
This coursework has set us with a task to; design, develop and test solutions for the London Underground system.  

## Task:
The following task summary is based on the document [Coursework_Spec.pdf](./resources/Coursework_Spec.pdf).  
- Task 1:
  - A:
    - Your team have been asked to provide a model software solution for a route planner of the London Underground tube system for use by the general public. You should provide a model that  will  determine  the  solution  for  the  quickest  journey  time  and  you  should  carefully consider the design, implementation and testing of the software.
    - For a user of the underground system, your solution needs to provide:
      1. The functionality to quickly and efficiently elicit the information from the customer for a planned route.
      2. Provide a list of stations showing how the customer will travel from one starting station `x` to the destination station `y` on the underground system.
      3. How long the journey will take in total.
  - B:
    - Your team also has to provide the histogram of (quickest) journey times between each pair of stations.

- Task 2:
  - A:
    - Due to a certain reason, the government has to consider closing tube lines between immediate neighbouring stations as many as possible, while meeting the following condition:
      1. A journey between any pair of stations should be still possible. For instance, even if the line between immediate neighbouring stations, Piccadilly Circus and Green Park, is closed, the journey between those two stations should be still possible on a different route.
    - Your team has been asked to provide a model software solution to assist the government with the decision:
      1. If the closure meeting the condition is not feasible, justify the conclusion.
      2. If the closure is feasible, provide a set of the closed lines by specifying a  pair of immediate neighbouring stations per line; e.g. Piccadilly Circus -- Green Park, if the line connecting these immediate neighbouring stations is closed.

- Task 3:
  - Your team is also asked to come up with your own idea to augment Task 1 or 2. An alternative is to come up with a new task related to the London Underground Data, which would require an algorithm that is different from those used for Tasks 1 and 2; you may use an algorithm that is not covered during the lectures but use an existing (library) code for it.
  - For instance, to augment Task 1, you may include an additional feature of a table or graphic showing the list of stations from start to destination with corresponding times of how long it will take: a table or graphic showing the list of stations from start to destination with corresponding times of how long it will take: travel time to next station, etc. To get a higher mark, you may **NOT** use the example of the table/graphic idea but use something else of your own. You should carefully consider the design, implementation and testing of the software based on your own idea.

## Code glossary:
### Task 3:
For this task I have written a web-app that allows you to create, edit and visualise graphs as well as step through the algorithms process.

### Miscellaneous:
I had also written a few other bits in C# to again assist in the creation of the main bits of code, a summary of these files can be found in the [tools README.md glossary here](./tools/README.md).

## References:
This section contains a list of references that I used to help me with parts of this code.
| Reference | Author | Used in |
| --- | --- | --- |
| COMP1828 "Graph 2.pptx" slide 30 | University Of Greenwich | [dijkstras_algorithm.ts](./tools/GraphBuilder/src/algorithms/dijkstras_algorithm.ts) |
| Newtonsoft.Json | [James Newton-King](https://github.com/JamesNK/Newtonsoft.Json) | [csvToJson.csx](./tools/csvToJson.csx) |
| Tesseract | [Tesseract](https://github.com/tesseract-ocr/tesseract) | [C# Implementation](https://github.com/charlesw/tesseract) | [csvToJson.csx](./tools/csvToJson.csx) |

## Author and license:
This project was created by Tristan Read (a.k.a. ReadieFur).  
This project is licensed under the GPL-3.0 license, a copy of this license can be found in the [LICENSE](./LICENSE) file.
