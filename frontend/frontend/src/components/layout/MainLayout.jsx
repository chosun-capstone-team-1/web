import React from 'react';
import { useMediaQuery } from 'react-responsive';
import MainLayoutPC from './MainLayoutPC';
import MainLayoutMobile from './MainLayoutMobile';

export default function MainLayout() {
  const isMobile = useMediaQuery({ maxWidth: 760 });
  return isMobile ? <MainLayoutMobile /> : <MainLayoutPC />;
}
