<script setup>
import { ref, nextTick } from 'vue';
import { router } from '@inertiajs/vue3';

const isOpen = ref(false);
const userInput = ref('');
const messages = ref([]);
const isLoading = ref(false);
const messagesContainer = ref(null);
const apiError = ref(null);

const predefinedQuestions = [
    'What is this site about?',
    'How do I search?',
    'Can I save articles?'
];

const toggleBot = () => {
    isOpen.value = !isOpen.value;
    if (isOpen.value && messages.value.length === 0) {
        // Add initial welcome message
        addMessage('bot', 'Hello! How can I help you today? You can ask me a question or select one below.');
    }
};

const addMessage = (sender, text) => {
    messages.value.push({ sender, text, id: Date.now() });
    scrollToBottom();
};

const scrollToBottom = () => {
    nextTick(() => {
        if (messagesContainer.value) {
            messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
        }
    });
};

const sendMessage = async (question = null) => {
    const textToSend = question || userInput.value.trim();
    if (!textToSend) return;

    addMessage('user', textToSend);
    userInput.value = '';
    isLoading.value = true;
    apiError.value = null;

    router.post(route('ai.ask'), {
        question: textToSend,
    }, {
        preserveScroll: true,
        preserveState: true,
        only: ['aiBotAnswer'],
        onSuccess: (page) => {
            if (page.props.aiBotAnswer) {
                 addMessage('bot', page.props.aiBotAnswer);
            } else {
                 addMessage('bot', 'Received a response, but could not find the answer.');
                 console.warn('AI bot answer prop missing in response:', page.props);
            }
            apiError.value = null;
        },
        onError: (errors) => {
            console.error("Error asking AI via Inertia:", errors);
            const firstError = Object.values(errors)[0] || "Sorry, I encountered an error. Please try again later.";
            addMessage('bot', firstError);
            apiError.value = firstError;
        },
        onFinish: () => {
            isLoading.value = false;
        },
    });
};

</script>

<template>
    <div>
        <!-- Floating Action Button -->
        <button 
            @click="toggleBot"
            class="fixed bottom-6 right-6 bg-primary dark:bg-primary-light text-white dark:text-gray-900 rounded-full p-4 shadow-lg hover:bg-primary-dark dark:hover:bg-primary focus:outline-none focus:ring-2 focus:ring-primary-dark dark:focus:ring-primary focus:ring-offset-2 dark:focus:ring-offset-gray-800 transition-transform duration-200 ease-out z-50"
            aria-label="Toggle Chat Bot"
        >
             <!-- Chat Icon -->
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
        </button>

        <!-- Chat Window -->
         <transition
            enter-active-class="transition ease-out duration-200"
            enter-from-class="transform opacity-0 scale-95 translate-y-4"
            enter-to-class="transform opacity-100 scale-100 translate-y-0"
            leave-active-class="transition ease-in duration-150"
            leave-from-class="transform opacity-100 scale-100 translate-y-0"
            leave-to-class="transform opacity-0 scale-95 translate-y-4"
        >
            <div 
                v-if="isOpen"
                class="fixed bottom-24 right-6 w-80 h-96 bg-white dark:bg-gray-800 rounded-lg shadow-xl flex flex-col border border-gray-200 dark:border-gray-700 z-40 overflow-hidden"
            >
                <!-- Header -->
                <div class="bg-gray-100 dark:bg-gray-700 p-3 flex justify-between items-center border-b border-gray-200 dark:border-gray-600">
                    <h3 class="font-semibold text-gray-800 dark:text-gray-100">Help Bot</h3>
                    <button @click="toggleBot" class="text-gray-500 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200">
                        <!-- Close Icon -->
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>

                <!-- Messages -->
                <div ref="messagesContainer" class="flex-1 overflow-y-auto p-4 space-y-3">
                    <div v-for="message in messages" :key="message.id">
                         <div 
                            :class="[
                                'p-2 rounded-lg max-w-[80%]',
                                message.sender === 'bot' ? 'bg-gray-200 dark:bg-gray-600 text-gray-800 dark:text-gray-100 text-left' : 'bg-primary dark:bg-primary-light text-white dark:text-gray-900 ml-auto text-right'
                            ]"
                        >
                            {{ message.text }}
                        </div>
                    </div>
                    <div v-if="isLoading" class="flex justify-start">
                         <span class="p-2 rounded-lg bg-gray-200 dark:bg-gray-600 text-gray-500 dark:text-gray-400 text-sm italic">
                             Bot is typing...
                         </span>
                     </div>
                    <!-- Show API Error if exists -->
                     <div v-if="apiError && !isLoading" class="flex justify-start">
                         <span class="p-2 rounded-lg bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 text-sm">
                             Error: {{ apiError }}
                         </span>
                     </div>
                    <!-- Predefined Questions for Bot -->
                    <div v-if="messages.length === 1 && messages[0].sender === 'bot'" class="mt-4 pt-2 border-t border-gray-200 dark:border-gray-600">
                         <p class="text-xs text-gray-500 dark:text-gray-400 mb-2">Or select a question:</p>
                         <button 
                            v-for="q in predefinedQuestions" 
                            :key="q"
                            @click="sendMessage(q)"
                            class="block w-full text-left text-sm text-primary dark:text-primary-light hover:underline p-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 mb-1"
                        >
                             {{ q }}
                         </button>
                     </div>
                </div>

                <!-- Input Area -->
                <div class="p-3 border-t border-gray-200 dark:border-gray-600 flex items-center gap-2 bg-gray-50 dark:bg-gray-700">
                    <input 
                        v-model="userInput"
                        type="text"
                        placeholder="Type your message..."
                        class="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-500 rounded-full bg-white dark:bg-gray-600 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-primary dark:focus:ring-primary-light focus:border-primary dark:focus:border-primary-light text-sm"
                        @keyup.enter="sendMessage()"
                        :disabled="isLoading"
                    >
                    <button 
                        @click="sendMessage()"
                        :disabled="isLoading || !userInput.trim()"
                        class="bg-primary dark:bg-primary-light text-white dark:text-gray-900 rounded-full p-2 disabled:opacity-50"
                        aria-label="Send Message"
                    >
                         <!-- Send Icon -->
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 transform rotate-90" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                        </svg>
                    </button>
                </div>
            </div>
         </transition>
    </div>
</template> 