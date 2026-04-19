// Blog post detail page — rendered at /blog/:slug.

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
  params?: RouteParams,
): Promise<void> {
  const slug = params?.slug ?? '';
  const post = BLOG_POSTS.find((p) => p.slug === slug);

  if (!post) {
    container.innerHTML = `
      <div class="blog-post-page">
        <a href="/blog" class="blog-back-link" data-link>
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6z"/>
          </svg>
          Back to Blog
        </a>
        <p class="blog-post-not-found">Post not found.</p>
      </div>
    `;
    return;
  }

  container.innerHTML = `
    <div class="blog-post-page">
      <a href="/blog" class="blog-back-link" data-link>
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M15.41 16.59L10.83 12l4.58-4.59L14 6l-6 6 6 6z"/>
        </svg>
        Back to Blog
      </a>
      <article class="blog-post-article">
        <header class="blog-post-header">
          <p class="blog-post-date">${formatDate(post.date)}</p>
          <h1 class="blog-post-title">${post.title}</h1>
        </header>
        <div class="blog-post-content">
          ${post.content}
        </div>
      </article>
    </div>
  `;
}
