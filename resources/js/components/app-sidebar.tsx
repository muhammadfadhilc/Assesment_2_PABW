import { Link } from '@inertiajs/react';
import { AlertTriangle, Building2, LayoutGrid, UserRound } from 'lucide-react';
import AppLogo from '@/components/app-logo';
import { NavMain } from '@/components/nav-main';
import { NavUser } from '@/components/nav-user';
import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarMenu, SidebarMenuButton, SidebarMenuItem } from '@/components/ui/sidebar';
import type { NavItem } from '@/types';
export function AppSidebar() {
  const links:NavItem[] = [
    { title:'Dashboard',href:'/dashboard',icon:LayoutGrid },
    { title:'Katalog',href:'/katalog',icon:Building2 },
    { title:'Setoran',href:'/setoran',icon:AlertTriangle },
    { title:'Profil Saya',href:'/profil',icon:UserRound },
  ];
  return <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader><SidebarMenu><SidebarMenuItem><SidebarMenuButton size="lg" asChild><Link href="/dashboard" prefetch><AppLogo/></Link></SidebarMenuButton></SidebarMenuItem></SidebarMenu></SidebarHeader>
      <SidebarContent><NavMain items={links}/></SidebarContent>
      <SidebarFooter><NavUser/></SidebarFooter>
  </Sidebar>;
}
