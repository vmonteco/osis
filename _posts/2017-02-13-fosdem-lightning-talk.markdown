---
layout: post
title:  "OSIS Presentation at FOSDEM 2017"
date:   2017-02-13 06:00:00
categories: community conference presentation
---

If you attended our [talk at FOSDEM'2017][1], you're well aware that the
Catholique University of Louvain (Université catholique de Louvain - UCL) has
decided to rewrite their core business applications in Python/Django, abandon
the slow evolution and poor scalability of the JavaEE platform, and make the new
application freely available as open source software. The talk shared with the
community the experience on building OSIS, the open source transition, the
cultural and technical shift, the engagement of students, teachers and employees
on the improvement of their own user experience, the costs implied and the
productivity gains.

<img src="{{ site.url }}/assets/posts/fosdem-mendonca.jpg"
alt="Hildeberto Mendonça presenting OSIS at FOSDEM">

The first release of OSIS happened a year ago, on January 31, 2016. We can say
that this presentation is the celebration of its first anniversary. During this
period, we have had great and tough moments. The greatest moment was the release
of the [score encoding][2] app that has helped to save an enormous amount of
time for teachers and administrative staff, by modernizing a previously
paper-based process. The toughest one was the struggle to implement the
admission process, revealing that the business complexity is still challenging,
despite the simplification of the technical part. But along the way, we have had
many more wins than failures, given that most of the problems we've faced in the
past are now solved.

The full technical shift may seem radical for many, but the transition from
Java to Python was the easiest part. Python allowed us to get rid of slow
compilations, long redeployments, verbose code and a complex type system. The
productivity skyrocketed instantaneously. Python is so straightforward that
we've trained the team on the fly, with almost no evangelization discourse.
Nowadays, when we have to maintain the old Java system people feel disappointed,
eager to come back to Python. Django is actually the perfect replacement for
JavaEE. We get the entire administration for free and write just enough custom
features to improve the user experience.

<img src="{{ site.url }}/assets/posts/osis-studies-administration.png"
alt="OSIS administration interface based on Django Admin">

On the other hand, being motivated about a technology and starting a project
from scratch didn't accredit us to open up the code right away. Nevertheless, we
did it, in a GitHub repository since the very first line of code. As a knowledge
engine, UCL wanted to see how much better the university would become in terms
of efficiency if all the processes and functionalities were openly available for
constant evaluations and contributions from the academic community, instead of
closed to a group of experienced users who have valuable knowledge about the
business, but little knowledge about how people actually use the application on
the field. The university also wanted to:

* inspire entrepreneurs to build integrated services to improve students
  academic experience;
* empower departments, endowed with the necessary expertise, to fulfill their
  particular needs by extending OSIS;
* build up students' experience on real world projects to boost their chances
  when applying for a job or founding a company; and
* reduce maintenance cost thanks to the stack of reliable open source products
  required by the application.

At the beginning, the development team had a lot to learn about this new thing
called [Open Source Software (OSS)][3]. They were hardcoding references to
internal resources, writing code in French instead of English, leaving confusing
comments for people out of context, badly formatted code, forgetting to add the
license on the top of the files and all sorts of things, exactly like they used
to do in the past. Fortunately, GitHub offers pull requests and we were able to
review contributions before they got public. Over time, the culture changed and
all these problems are gone.

As the project evolved, it started calling attention of the academic community.
We had the chance to present the project several times for academic and
administrative staff, generating new opportunities such as:

* A group of faculties decided to contribute with an application to manage
  dissertations and theses. More and more faculties are joining the initiative.
* The faculty of medicine contributed with an app to manage internships.
* An administrative department will soon manage the assignment of research
  assistants.
* INGInious, another open source project developed in the computer science
  department to conduct online programming exams, will soon submit the scores of
  the students directly to the score encoding app.

Many other additional applications will be under discussions in the coming
months. That's an amount of work our fixed team of 5 programmers wouldn't be
able to do. Being open source attracted contributions from 13 additional
individuals as well as the engagement of the Université Saint-Louis in Brussels,
saving lots of money and time.

<img src="{{ site.url }}/assets/posts/osis-admission.png"
alt="The Frontoffice part of OSIS">

We wish many other higher education institutions would join OSIS in the future to
build the state of the art of student's lifecycle management. This extends from
the admission to the diploma and all information orbiting this fundamental
process, such as planning the academic year, managing partnerships with other
institutions for exchange and mobility programs, assigning teachers to courses
and courses to students, etc. Any knowledge and technical exchange would be
extremely valuable.

Last, but not least, we would like to thank FOSDEM's team for the excellent
organization and for attracting so many smart people from all over Europe!

[1]: http://uclouvain.github.io/osis/community/conference/presentation/2017/01/03/fosdem-lightning-talk.html
[2]: http://uclouvain.github.io/osis/release/scores/2016/06/01/score-encoding.html
[3]: https://opensource.org
