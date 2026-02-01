import React from 'react';
import { Outlet } from 'react-router-dom';
import Navbar from './Navbar';
import Sidebar from './Sidebar';

const Layout: React.FC = () => {
    return (
        <div className="min-h-screen bg-zinc-50 text-zinc-900 font-sans">
            <Navbar />
            <div className="flex">
                <Sidebar />
                <main className="flex-1 p-6 h-[calc(100vh-4rem)] overflow-y-auto">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default Layout;
