<template>
  <aside
    class="bg-gray-800 text-gray-100 space-y-2 py-4 fixed inset-y-0 left-0 transform -translate-x-full md:relative md:translate-x-0 transition-all duration-300 ease-in-out z-30 flex flex-col sticky top-0 h-screen"
    :class="{
      'translate-x-0': isMobileOpen, 
      'w-64': isDesktopExpanded,
      'w-20': !isDesktopExpanded,
    }"
  >
    <div class="px-4 flex items-center justify-between h-12 mb-2 border-b border-gray-700 pb-2 md:pb-4">
      <Link :href="route('home')" v-show="isDesktopExpanded" class="flex items-center truncate">
        <ApplicationLogo class="block h-8 w-auto fill-current text-gray-200 mr-2 shrink-0" />
        <h2 class="text-xl font-semibold text-white transition-opacity duration-200 whitespace-nowrap overflow-hidden" 
            :class="{ 'opacity-0': !isDesktopExpanded, 'opacity-100': isDesktopExpanded }">
          CraftyX Hub
        </h2>
      </Link>
       <div v-show="!isDesktopExpanded" class="w-full flex justify-center">
         <Link :href="route('home')">
            <ApplicationLogo class="block h-8 w-auto fill-current text-gray-200" />
         </Link>
       </div>
      <button @click="toggleDesktopExpand" class="hidden md:block text-gray-400 hover:text-white p-1 rounded focus:outline-none focus:ring-2 focus:ring-gray-500">
        <ChevronDoubleLeftIcon v-if="isDesktopExpanded" class="h-6 w-6" />
        <ChevronDoubleRightIcon v-else class="h-6 w-6" />
      </button>
    </div>

    <nav class="flex-grow overflow-y-auto px-2 space-y-1">
      <ul v-if="navItems && navItems.length > 0">
        <li v-for="(item, index) in navItems" :key="item.label + index">
          <a v-if="!item.children || item.children.length === 0" 
             :href="item.href" 
             class="flex items-center px-3 py-2.5 rounded-md hover:bg-gray-700 text-gray-300 hover:text-white transition duration-150 group text-sm font-medium"
             :class="{ 'bg-gray-900 text-white': isActive(item.activeRoutes) }"
             :title="isDesktopExpanded ? '' : item.label"
             @click.prevent="navigateToUrl(item.href)">
            <span v-if="item.icon" class="h-5 w-5 shrink-0 transition-all duration-300" :class="isDesktopExpanded ? 'mr-3' : 'mx-auto'">
              <component :is="iconRegistry[item.icon]" v-if="iconRegistry[item.icon]" class="h-full w-full"/>
              <span v-else class="w-full h-full flex items-center justify-center text-xs font-semibold">{{ item.icon.substring(0,1) }}</span>
            </span>
            <span class="transition-all duration-200 whitespace-nowrap overflow-hidden"
                  :class="{ 'opacity-0 w-0 ml-0': !isDesktopExpanded, 'opacity-100': isDesktopExpanded }"
                  v-show="isDesktopExpanded">
                {{ item.label }}
            </span>
          </a>
          <div v-else>
            <button @click="toggleExpandableSection(item.label)" 
                    class="flex items-center justify-between w-full px-3 py-2.5 rounded-md hover:bg-gray-700 text-gray-300 hover:text-white transition duration-150 group text-sm font-medium focus:outline-none"
                    :class="{ 'bg-gray-750': isSectionActive(item) && !expandedSections[item.label] }">
              <div class="flex items-center">
                <span v-if="item.icon" class="h-5 w-5 shrink-0 transition-all duration-300" :class="isDesktopExpanded ? 'mr-3' : 'mx-auto'">
                  <component :is="iconRegistry[item.icon]" v-if="iconRegistry[item.icon]" class="h-full w-full" />
                  <span v-else class="w-full h-full flex items-center justify-center text-xs font-semibold">{{ item.icon.substring(0,1) }}</span>
                </span>
                <span class="transition-all duration-200 whitespace-nowrap overflow-hidden" 
                      :class="{ 'opacity-0 w-0 ml-0': !isDesktopExpanded, 'opacity-100': isDesktopExpanded }"
                      v-show="isDesktopExpanded">
                    {{ item.label }}
                </span>
              </div>
              <ChevronRightIcon v-if="isDesktopExpanded" class="h-4 w-4 text-gray-400 group-hover:text-gray-200 transition-transform duration-200 transform shrink-0" :class="{ 'rotate-90': expandedSections[item.label] }" />
            </button>
            <transition name="expand">
                <ul v-show="expandedSections[item.label] && isDesktopExpanded" class="mt-1 space-y-1 ml-1 pl-7 border-l border-gray-700/50 py-1">
                    <li v-for="child in item.children" :key="child.label">
                        <a :href="child.href"
                            class="flex items-center px-3 py-2 rounded-md hover:bg-gray-700 text-gray-400 hover:text-white transition duration-150 group text-xs font-medium"
                            :class="{ 'bg-gray-900 text-white': isActive(child.activeRoutes) }"
                            :title="isDesktopExpanded ? '' : child.label"
                            @click.prevent="navigateToUrl(child.href)">
                            <span v-if="child.icon" class="h-4 w-4 shrink-0 transition-all duration-300" :class="isDesktopExpanded ? 'mr-2' : 'mx-auto'">
                               <component :is="iconRegistry[child.icon]" v-if="iconRegistry[child.icon]" class="h-full w-full" />
                               <span v-else class="w-full h-full flex items-center justify-center text-xs font-semibold">{{ child.icon.substring(0,1) }}</span>
                            </span>
                             <span class="transition-all duration-200 whitespace-nowrap overflow-hidden" 
                                  :class="{ 'opacity-0 w-0 ml-0': !isDesktopExpanded, 'opacity-100': isDesktopExpanded }"
                                  v-show="isDesktopExpanded">
                                {{ child.label }}
                            </span>
                        </a>
                    </li>
                </ul>
            </transition>
          </div>
        </li>
      </ul>
       <div v-else class="px-2 py-2 text-gray-500">
        <span v-if="isDesktopExpanded">Loading nav...</span>
        <span v-else class="block h-6 w-6 mx-auto">...</span>
      </div>
    </nav>
  </aside>
</template>

<script setup>
import { defineProps, ref, reactive, watch, onMounted, computed } from 'vue';
import { Link, usePage, router } from '@inertiajs/vue3';
import ApplicationLogo from '@/Components/ApplicationLogo.vue';
import {
    HomeIcon,
    UsersIcon,
    UserGroupIcon,
    ShieldCheckIcon,
    DocumentDuplicateIcon,
    ListBulletIcon,
    PlusCircleIcon,
    ClockIcon,
    RectangleStackIcon, // Replaced CollectionIcon
    TagIcon,
    ChevronDoubleLeftIcon,
    ChevronDoubleRightIcon,
    ChevronRightIcon
} from '@heroicons/vue/24/outline';

const props = defineProps({
  navItems: {
    type: Array,
    default: () => [],
  },
  isMobileOpen: { 
    type: Boolean,
    default: false,
  }
});

const isDesktopExpanded = ref(true);
const page = usePage();
const expandedSections = reactive({});

const initializeExpandedSections = () => {
  props.navItems.forEach(item => {
    if (item.children && item.children.length > 0) {
      const isParentActive = item.children.some(child => isActive(child.activeRoutes));
      expandedSections[item.label] = isParentActive;
    }
  });
};

onMounted(initializeExpandedSections);
watch(() => props.navItems, initializeExpandedSections, { deep: true });

const toggleDesktopExpand = () => {
  isDesktopExpanded.value = !isDesktopExpanded.value;
};

const toggleExpandableSection = (label) => {
  if (!isDesktopExpanded.value) { // If sidebar is collapsed, expand it first
      isDesktopExpanded.value = true;
  }
  expandedSections[label] = !expandedSections[label];
};

// Use direct window.location.href for all navigation to ensure it works
// regardless of route context or namespace transitions
const navigateToUrl = (url) => {
  console.log(`Navigating to: ${url}`);
  window.location.href = url;
};

function isActive(activeRoutes) {
  if (!activeRoutes || !page.props.ziggy || !page.props.ziggy.route_name) return false;
  
  const currentRouteName = page.props.ziggy.route_name;
  const isAdmin = page.props.auth.isAdmin;
  
  return activeRoutes.some(route => {
    // Exact match
    if (currentRouteName === route) return true;
    
    // Starts with route prefix
    if (currentRouteName.startsWith(route + '.')) return true;
    
    // Special case for admins - if on editor routes but clicking admin routes
    if (isAdmin && currentRouteName.startsWith('editor.') && route.startsWith('admin.')) {
      // Map between editor and admin route prefixes
      const editorToAdminMap = {
        'editor.posts': 'admin.posts',
        'editor.categories': 'admin.categories',
        'editor.tags': 'admin.tags'
      };
      
      // Extract the current route's base prefix (e.g., 'editor.posts.create' -> 'editor.posts')
      const editorPrefix = currentRouteName.split('.').slice(0, 2).join('.');
      const adminEquivalent = editorToAdminMap[editorPrefix];
      
      // Check if the target admin route matches the equivalent admin route for current editor route
      return adminEquivalent && route.startsWith(adminEquivalent);
    }
    
    return false;
  });
};

const isSectionActive = (section) => {
    if (!section.children) return false;
    return section.children.some(child => isActive(child.activeRoutes));
};

const iconRegistry = {
  HomeIcon,
  UsersIcon,
  UserGroupIcon,
  ShieldCheckIcon,
  DocumentDuplicateIcon,
  ListBulletIcon,
  PlusCircleIcon,
  ClockIcon,
  RectangleStackIcon, 
  TagIcon,
  // Chevron icons are used directly in template
};

</script>

<style scoped>
aside {
  height: 100vh;
  position: sticky;
  top: 0;
}
nav {
  &::-webkit-scrollbar {
    width: 4px;
  }
  &::-webkit-scrollbar-thumb {
    background: #4A5568; /* Tailwind gray-600 */
    border-radius: 4px;
  }
  &::-webkit-scrollbar-track {
    background: transparent;
  }
}

.opacity-0.w-0.ml-0 {
    opacity: 0 !important;
    width: 0 !important;
    font-size:0 !important;
    margin-left: 0 !important;
}

.expand-enter-active,
.expand-leave-active {
  transition: all 0.2s ease-in-out;
  max-height: 500px; 
  overflow: hidden;
}
.expand-enter-from,
.expand-leave-to {
  opacity: 0;
  max-height: 0;
  /* transform: translateY(-5px); */ /* Optional subtle movement */
}
</style> 