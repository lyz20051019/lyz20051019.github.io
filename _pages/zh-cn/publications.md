---
page_id: publications
layout: page
permalink: /publications/
title: 出版物
description: 按类别分类的出版物，按时间顺序排列（由 jekyll-scholar 生成）
nav: true
nav_order: 3
---

{% include bib_search.liquid %}

<!-- 排序按钮 -->
<div style="margin:0 0 1.5rem; text-align:right;">
  <button id="toggleSort" class="btn btn-sm btn-primary">最新优先 ↓</button>
</div>

<!-- 文献容器 -->
<div class="publications">
  {% bibliography %}
</div>

<script>
document.addEventListener('DOMContentLoaded', () => {
  const container = document.querySelector('.publications');
  const btn = document.getElementById('toggleSort');
  let isNewestFirst = true;

  // ======================================
  // 1. 收集年份分组
  // ======================================
  const groups = [];
  const yearHeadings = document.querySelectorAll('h2.bibliography');
  
  yearHeadings.forEach(heading => {
    const list = heading.nextElementSibling;
    if (list && list.tagName === 'OL') {
      groups.push({
        wrapper: [heading, list],
        year: parseInt(heading.textContent.replace(/\D/g, ''))
      });
    }
  });

  // ======================================
  // 2. 全局编号：严格 2017→2026 递增（核心原则不动）
  // ======================================
  let num = 1;
  [...groups].sort((a, b) => a.year - b.year).forEach(group => {
    // 正常分配全局编号（年份越早编号越小）
    group.wrapper[1].querySelectorAll('li').forEach(li => {
      const col = li.querySelector('.col-sm-8');
      if (col) {
        col.querySelector('.bib-number')?.remove();
        col.insertAdjacentHTML('afterbegin', `<span class="bib-number">${num}.</span>`);
        num++;
      }
    });

    // 🔥 唯一修改：组内文献DOM反转显示（仅视觉改变，编号完全不变）
    const lis = group.wrapper[1].querySelectorAll('li');
    lis.forEach(li => group.wrapper[1].prepend(li));
  });

  // ======================================
  // 3. 核心排序功能（完全不变）
  // ======================================
  function renderGroups() {
    container.innerHTML = '';
    
    const sorted = isNewestFirst
      ? [...groups].sort((a, b) => b.year - a.year)
      : [...groups].sort((a, b) => a.year - b.year);
    
    sorted.forEach(group => {
      container.appendChild(group.wrapper[0]);
      container.appendChild(group.wrapper[1]);
    });
    
    // 中文按钮文字
    btn.textContent = isNewestFirst ? '最新优先 ↓' : '最早优先 ↑';
  }

  btn.addEventListener('click', () => {
    isNewestFirst = !isNewestFirst;
    renderGroups();
  });

  renderGroups();
});
</script>