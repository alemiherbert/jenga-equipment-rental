import './site-navigation';
import './theme-switcher';
import './theme-detection';
import './featured-equipment';
import carousel from './carousel';
import featuredEquipment from './featured-equipment';
import Alpine from 'alpinejs';
import focus from '@alpinejs/focus'
// import searchComponent from './components/search';

window.Alpine = Alpine;
// window.searchComponent = searchComponent;
Alpine.plugin(focus)
Alpine.data('carousel', carousel);
Alpine.data('featuredEquipment', featuredEquipment);
Alpine.start();