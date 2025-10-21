---
title: "Home"
layout: "magazine"

sections:
  - type: hero
    limit: 4
    query:
      section: posts
      where:
        featured: true

  - type: grid
    title: "Ultime notizie"
    limit: 8
    query:
      section: posts

  - type: grid
    title: "Prove su strada"
    limit: 6
    query:
      category: "prove"

  - type: grid
    title: "Elettrico"
    limit: 6
    query:
      category: "elettrico"

  - type: grid
    title: "Guide & Consigli"
    limit: 6
    query:
      category: "guide"

  - type: grid
    title: "Mercato"
    limit: 6
    query:
      category: "mercato"
---
