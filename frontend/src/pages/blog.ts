// Blog listing page — rendered at /blog.

import { RouteParams } from '../router';
import { BLOG_POSTS } from '../data/blog-posts';

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString('en-GB', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
}

export async function render(
  container: HTMLElement,
  _params?: RouteParams,
): Promise<void> {
  const cards = BLOG_POSTS.map(
    (post) => `
    <a href="/blog/${post.slug}" class="blog-card" data-link>
      <div class="blog-card-body">
        <p class="blog-card-date">${formatDate(post.date)}</p>
        <h2 class="blog-card-title">${post.title}</h2>
        <p class="blog-card-preview">${post.preview}</p>
      </div>
      <div class="blog-card-footer">
        Read more
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z"/>
        </svg>
      </div>
    </a>
  `,
  ).join('');

  container.innerHTML = `
    <div class="blog-page">
      <header class="blog-page-header">
        <h1 class="blog-page-title">Blog</h1>
        <p class="blog-page-sub">Insights on solar energy, simulation methodology, and financial analysis.</p>
      </header>
      <div class="blog-grid">
        ${cards}
      </div>
    </div>
  `;
}
