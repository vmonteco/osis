---
layout: post
title:  "OSIS Presentation at FOSDEM 2017"
date:   2017-02-03 06:00:00
categories: community conference presentation
---

If you attended our talk at FOSDEM'2017, you're well aware that the Catholique University of Louvain (Université catholique de Louvain - UCL) has decided to
rewrite their core business applications in Python/Django, abandon the slow
evolution and poor scalability of the JavaEE platform and make the new
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
admission process, which revealed the fragility of our management style. But
along the way, we have had many more wins than failures. Among all the problems
we had in the past, we can confidently say that we are almost done with them.

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

OSIS (Open Student Information System) is an application designed to manage the
core business of higher education institutions. It is free and open source under
the terms of GPL v3 public license, aligned with the strong spirit of knowledge
sharing and collaboration with the community. The project is sponsored by
Université catholique de Louvain (UCL) in the context of its long term goal of
modernising its information systems towards the next generation of students,
devices, practices and technologies.

We aim that UCL and many other higher education institutions adopt OSIS to be
able to maintain, control and monitor the entire student’s career. This extends
from the admission to the diploma and all information orbiting this fundamental
process, such as planning the academic year, managing partnerships with other
institutions for exchange and mobility programs, assigning teachers to courses
and courses to students, etc. At the current stage, OSIS is designed to fulfil
UCL’s needs, but it can be properly adapted to fulfil more needs coming from
other institutions interested in joining the project, which is the case of
Université Saint-Louis, Bruxelles.

For us, offering a reusable system is not the only advantage of being open
source. It also means:

* fully transparent operations for the entire academic community;
* inspiration for entrepreneurs to build integrated services to improve students
  academic experience;
* empower departments, endowed with the necessary expertise, to fulfill their
  particular needs by extending OSIS;
* build up students' experience on real world projects to boost their chances
  when applying for a job or founding a company; and
* reduced maintenance cost for the University thanks to the range of reliable
  open source products required by the application.

But the path to open source was not simple. It required lots of discussions to
finally find a realistic long term formula to meet the institution's major
goals. Now that it is our reality, this history cannot be kept aside, but shared
with FOSDEM's community. We are going to answer the following questions during
the presentation:

* Why we are sharing our core business applications before any other higher
  education institution.
* How the academic community persuaded us to use Python/Django/PostgreSQL
  instead of JavaEE.
* How we are adapting to this new reality that requires much more discipline and
  high quality craftsmanship work.
* Why there is no doubt we will succeed in this entrepreneurship.
* Why we need your help to better manage and write this open source software.
