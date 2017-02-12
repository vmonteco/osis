---
layout: post
title:  "OSIS Presentation at FOSDEM 2017"
date:   2017-02-03 06:00:00
categories: community conference presentation
---

If you attended our talk at FOSDEM'2017, you're well aware that the Catholique
University of Louvain (Université catholique de Louvain - UCL) has decided to
rewrite their core business applications in Python/Django, abandon the slow
evolution and poor scalability of the JavaEE platform, and make the new
application freely available as open source software. The talk shared with the
community the experience on building OSIS, the open source transition, the
cultural and technical shift, the engagement of students, teachers and employees
on the improvement of their own user experience, the costs implied and the
productivity gains.

The first release of OSIS happened a year ago, on January 31, 2016. We can say
that this presentation is the celebration of its first anniversary. During this
period, we have had great and tough moments. The greatest moment was the release
of the score encoding app that has helped to save an enormous amount of time
of teachers and administrative staff, by modernizing a previously manual and
paper-based process. The toughest one was the struggle to implement the
admission process, revealing that despite the simplification of the technical
part the business complexity is still challenging. But along the way, we have
had many more wins than failures. Most of problems we've faced in the past are
now solved and 
Among all the problems we've had in the past, we can confidently say that we are almost done with them.

The full technical shift may seem radical for many, but the transition from
Java to Python was the easiest part. Python allowed us to get rid of slow
compilations, long redeployments, verbose code and a complex type system. The
productivity skyrocketed instantaneously and all we had to do was to train the
team on the fly, with almost no evangelization discourse. Nowadays, when we have
to maintain the old system people get easily depressed, eager to come back to
Python. Django is actually the perfect replacement for JavaEE. We get the entire
administration for free and write just enough custom features to improve the
user experience.

<img src="{{ site.url }}/assets/posts/osis-studies-administration.png"
alt="OSIS administration interface based on Django Admin">

On the other hand, been motivated about a technology and starting a project from
scratch didn't accredited us to open up the code. Nevertheless, we did it, in a
GitHub repository since the very first line of code. As a knowledge engine, UCL
wanted to see how much better the university would become in terms of efficiency
if all the processes and functionalities were openly available for constant
evaluations and contributions from the academic community, instead of closed for
a group of opinionated authorities how have no or little knowledge about how
people actually works on the field. It also wanted to:

* inspire entrepreneurs to build integrated services to improve students
  academic experience;
* empower departments, endowed with the necessary expertise, to fulfill their
  particular needs by extending OSIS;
* build up students' experience on real world projects to boost their chances
  when applying for a job or founding a company; and
* reduce maintenance cost for the University thanks to the range of reliable
  open source products required by the application.

At the beginning, the development team had a lot to learn about this new thing
called open source. They were hardcoding references to internal resources,
writing code in french instead of english, leaving no-sense comments, badly
formatted code, forgetting to add the license on the top of the files and all
sorts of things, as they used to do in the past. Fortunately, GitHub offers pull
requests and we were able to review contributions before they got public. Over
time, all these problems were gone.

As the project evolved, it started calling attention of the academic community.
A week before going into production for general use, a computer science student
has detected a serious security flaw. We were not properly using Django security
and we spent the weekend fixing it. We were lucky to have his input. This would
not have happened if the project was not open source and we would be in big
trouble writing proprietary software. We had the chance to present the project
several times for academic and administrative staff and new opportunities
appeared from nowhere. As we were busy rewriting the old application:

* A group of faculties, with their own resources, decided to contribute with an
  application to manage dissertations and theses.
* The faculty of medicine contributed with an app to manage students'
  internships.
* An administrative department will son manage the assignment of teachers'
  assistants.
* INGInious, another open source project developed in the computer science
  department to conduct online programming exams, will soon submit the scores of
  the students directly to the assessment app.

Many other additional applications will be under discussion in the coming
months. That's an amount of work our fixed team of 5 programmers wouldn't be
able to do any time soon. Being open source attracted contributions from 14
individuals as well as the engagement of the Université Saint-Louis in Brussels,
saving lots of money and time.

<img src="{{ site.url }}/assets/posts/celebrating-first-general-availability.jpg"
alt="Celebrating the first general availability of OSIS">

We wish that many other higher education institutions join OSIS to build the
state of the art in terms of management of the entire student’s lifecycle. This
extends from the admission to the diploma and all information orbiting this
fundamental process, such as planning the academic year, managing partnerships
with other institutions for exchange and mobility programs, assigning teachers
to courses and courses to students, etc.


* How the academic community persuaded us to use Python/Django/PostgreSQL
  instead of JavaEE.
* How we are adapting to this new reality that requires much more discipline and
  high quality craftsmanship work.
* Why there is no doubt we will succeed in this entrepreneurship.
* Why we need your help to better manage and write this open source software.
