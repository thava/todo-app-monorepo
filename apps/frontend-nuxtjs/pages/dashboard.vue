<template>
  <div class="min-h-screen flex flex-col bg-background">
    <TopBar />

    <div class="flex flex-1">
      <Sidebar />

      <main class="flex-1 p-6 overflow-auto">
        <NuxtPage />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  middleware: 'auth',
});
</script>
