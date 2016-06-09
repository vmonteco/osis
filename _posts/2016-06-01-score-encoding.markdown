---
layout: post
title:  "Encoding the Scores of Thousands of Students"
date:   2016-06-01 06:00:00
categories: release scores
---

Today, we are glad to announce the very first operational release of OSIS. It
means it contains a minimal amount of features that can be used to automate one
of the processes of your higher education institution.

<img src="{{ site.url }}/assets/posts/score_encoding.png">

The process we are delivering today is called "Score Encoding", which is the one
we run to collect thousands of scores, from hundreds of teachers from all over
the campus, and from partner institutions spread all over the world. This
process usually starts right after the period of exams, that can be common to
the entire university or unique for each faculty.

Honestly, this is not the most expected functionality for those who want to
start using OSIS from day one. There are a lot of things that come first. But
the reason why the score encoding is coming sooner is rather simple: OSIS
is replacing an existing application that doesn't fulfill the needs of UCL
anymore. As we develop OSIS, we get anxious to see it in production as soon and
frequent as possible. But we cannot simply wait until all features of the old
application have their equivalence in the new application. It would take too
long and we know the risks of a waterfall process. So, we prioritized features
that are complementary to the old application instead of replacing something
right away.

## The Score Encoding Module

The score encoding app allows teachers to encode the scores of their students
after the exams. It is a critical process because the success of the students
depends on the correctness of the scores and on the security of the application.
It's important to offer a very good usability so teachers don't feel confused or
tired while encoding the scores. And once the scores are submitted, the
modification of those scores is carefully monitored.

There are three ways of encoding scores:

1. _on-line encoding_: the teacher fills in an on-line form for each one of his
   courses, encoding the scores directly in the application and making them
   immediately available for the faculty.
2. _spreadsheet encoding_: the teacher downloads a spreadsheet file for each
   one of his courses. The spreadsheet contains a list the enrolled students.
   Then (s)he fills in the spreadsheets with the scores and uploads the files
   back into OSIS to register the scores.
3. _paper encoding_: the application generates an A4 printable PDF file for
   each course and the teacher fills in the scores and send the paper form to
   the faculty. The faculty staff gets busy encoding scores from paper to OSIS.

<img src="{{ site.url }}/assets/posts/online_encoding.png">

The on-line encoding is definitely the one that allows the process to move
faster, but when there are too many students enrolled in a course - more than a
hundred students for instance - the user interface gets noisy with plenty of
fields. We will work hard in the future to improve its usability but we will
hardly do better than a spreadsheet. So, we suggest the spreadsheet when the
amount of students is high or when you want to work off-line for a while. At
last, the paper form is not recommended because it makes everybody work more
than necessary, but it's available anyway to cover any unforeseen situation.

To help minimizing encoding errors, OSIS also offers the possibility of
re-encoding the scores to detect differences from the initial attempt. It seems
odd to re-encode everything again, but we can assume that the probability of
making the same mistake twice in the same place is considerably lower, helping
to expose the mistakes of the first encoding.

<img src="{{ site.url }}/assets/posts/double_encoding.png">

## Living with the legacy

To put OSIS in the process pipeline, we had to export data from the current
database to the new one. The data was just enough to make the score encoding
work. When OSIS finishes collecting scores from all over the university we
transfer the scores to the old application so it can perform the next processes
in the sequence.

If you decide to adopt OSIS from the beginning, as we do, you should get ready
to inject data from your current application into OSIS, as well as re-injecting
back into your application the modifications made by OSIS. You have to keep
doing that for every new functionality. It's important that both applications do
not change the same data. It would make the exchange between them very hard to
implement. So, every time OSIS modifies business data it means it takes
ownership of the data and the old application doesn't modify that data anymore.

In the upcoming weeks we will work on the academic calendar, which is useful
for the score encoding because it defines the start and the end of the exam
sessions and the deadline to encode the scores.
