import SideNav from '@/app/components/sidenav/sidenav';
import { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Workspace"
};

export default async function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen flex-col md:flex-row md:overflow-hidden">
      <div className="w-full flex-none md:w-48 xlg:w-64">
        <SideNav />
      </div>
      <div className="flex-grow md:overflow-y-auto py-4 md:px-4">{children}</div>
    </div>
  );
}
