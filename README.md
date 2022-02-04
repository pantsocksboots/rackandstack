# rackandstack

A web application to manage data associated with assessment and selection (A&S) processes.

## Apps

### rubric

rubric is responsible for managing evolutions. Only administrators will have access to rubric's full CRUD functionality.

There are multiple types of evolutions available in rubric - Evolution, TimedEvolution, CountEvolution and PassFailEvolution. Regardless of type, all evolutions are linked to at least one Trait.

A Trait is what is being assessed or measured by the evolution, for example, Competence (strength, endurance, aerobic capacity, general knowledge) or Character (resilience, attitude, demeanor, team ability, etc).

### gradebook

gradebook is responsible for all things related to recording scores in the database. It will maintain 2 separate tables: TraitScores - a table of scores for subjective traits.
ObjectiveScores - a table of scores for the objective evolutions. All scores are stored as positive integers.
Timed Evolutions are stored in seconds, PassFail is 1 or 0. Count evolutions are the Rep Count.

### stucon

stucon - short for student control - is responsible for managing student records and assigning new student enrollments to blocks of training and cohorts.

### surveys

surveys encapsulates all of the peer evaluation capability of the rackandstack. The following survey types are available - Nominations, Perceptions, Peer Feedback, Top 5/Bottom 5, and Short Q&A.
