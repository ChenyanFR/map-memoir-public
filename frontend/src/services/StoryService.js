import { 
  collection, 
  doc, 
  addDoc, 
  updateDoc, 
  deleteDoc, 
  getDoc, 
  getDocs, 
  query, 
  where, 
  orderBy, 
  limit, 
  serverTimestamp 
} from 'firebase/firestore';
import { ref, uploadBytes, getDownloadURL, deleteObject } from 'firebase/storage';
import { db, storage } from '../config/firebase';
import toast from 'react-hot-toast';

export class StoryService {
  static async saveStory(userId, storyData) {
    try {
      // Clean the data to ensure it's serializable
      const cleanStoryData = JSON.parse(JSON.stringify(storyData));
      
      const story = {
        userId,
        title: cleanStoryData.title,
        description: cleanStoryData.description || '',
        content: cleanStoryData.content,
        place: cleanStoryData.place,
        theme: cleanStoryData.theme,
        isPublic: cleanStoryData.isPublic || false,  // Use user's choice
        customTags: cleanStoryData.customTags || [],
        createdAt: serverTimestamp(),
        updatedAt: serverTimestamp(),
        likes: 0,
        views: 0,
        tags: this.extractTags(cleanStoryData.content, cleanStoryData.place?.name)
      };

      console.log('Saving story to Firestore:', story);

      const docRef = await addDoc(collection(db, 'stories'), story);
      console.log('Story saved with ID:', docRef.id);
      
      toast.success('Story saved successfully!');
      return docRef.id;
    } catch (error) {
      console.error('Error saving story:', error);
      toast.error('Failed to save story');
      throw error;
    }
  }

  static async getUserStories(userId, limitCount = 20) {
    try {
      const q = query(
        collection(db, 'stories'),
        where('userId', '==', userId),
        orderBy('createdAt', 'desc'),
        limit(limitCount)
      );
      
      const querySnapshot = await getDocs(q);
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error fetching user stories:', error);
      toast.error('Failed to load your stories');
      throw error;
    }
  }

  static async getPublicStories(limitCount = 20) {
    try {
      const q = query(
        collection(db, 'stories'),
        where('isPublic', '==', true),
        orderBy('createdAt', 'desc'),
        limit(limitCount)
      );
      
      const querySnapshot = await getDocs(q);
      return querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
    } catch (error) {
      console.error('Error fetching public stories:', error);
      toast.error('Failed to load public stories');
      throw error;
    }
  }

  static async updateStory(storyId, updates) {
    try {
      const storyRef = doc(db, 'stories', storyId);
      await updateDoc(storyRef, {
        ...updates,
        updatedAt: serverTimestamp()
      });
      toast.success('Story updated successfully!');
    } catch (error) {
      console.error('Error updating story:', error);
      toast.error('Failed to update story');
      throw error;
    }
  }

  static async deleteStory(storyId) {
    try {
      // Delete the story document
      await deleteDoc(doc(db, 'stories', storyId));
      
      // TODO: Delete associated audio file from storage
      // await this.deleteAudioFile(storyId);
      
      toast.success('Story deleted successfully!');
    } catch (error) {
      console.error('Error deleting story:', error);
      toast.error('Failed to delete story');
      throw error;
    }
  }

  static async saveAudioFile(storyId, audioBlob) {
    try {
      const audioRef = ref(storage, `audio/${storyId}.wav`);
      const snapshot = await uploadBytes(audioRef, audioBlob);
      const downloadURL = await getDownloadURL(snapshot.ref);
      
      // Update story with audio URL
      await this.updateStory(storyId, { audioUrl: downloadURL });
      
      return downloadURL;
    } catch (error) {
      console.error('Error saving audio file:', error);
      toast.error('Failed to save audio file');
      throw error;
    }
  }

  static async deleteAudioFile(storyId) {
    try {
      const audioRef = ref(storage, `audio/${storyId}.wav`);
      await deleteObject(audioRef);
    } catch (error) {
      console.error('Error deleting audio file:', error);
      // Don't show error toast as this is usually called during cleanup
    }
  }

  static async toggleStoryPublic(storyId, isPublic) {
    try {
      await this.updateStory(storyId, { isPublic });
      toast.success(isPublic ? 'Story made public!' : 'Story made private!');
    } catch (error) {
      console.error('Error toggling story visibility:', error);
      toast.error('Failed to update story visibility');
      throw error;
    }
  }

  static async incrementViews(storyId) {
    try {
      const storyRef = doc(db, 'stories', storyId);
      const storyDoc = await getDoc(storyRef);
      
      if (storyDoc.exists()) {
        const currentViews = storyDoc.data().views || 0;
        await updateDoc(storyRef, { views: currentViews + 1 });
      }
    } catch (error) {
      console.error('Error incrementing views:', error);
      // Don't show error toast as this is a background operation
    }
  }

  static async likeStory(storyId, userId) {
    try {
      // Add to user's favorites
      await addDoc(collection(db, 'favorites'), {
        userId,
        storyId,
        createdAt: serverTimestamp()
      });

      // Increment story likes
      const storyRef = doc(db, 'stories', storyId);
      const storyDoc = await getDoc(storyRef);
      
      if (storyDoc.exists()) {
        const currentLikes = storyDoc.data().likes || 0;
        await updateDoc(storyRef, { likes: currentLikes + 1 });
      }

      toast.success('Added to favorites!');
    } catch (error) {
      console.error('Error liking story:', error);
      toast.error('Failed to like story');
      throw error;
    }
  }

  static async getUserFavorites(userId) {
    try {
      const q = query(
        collection(db, 'favorites'),
        where('userId', '==', userId),
        orderBy('createdAt', 'desc')
      );
      
      const querySnapshot = await getDocs(q);
      const favorites = [];
      
      for (const favoriteDoc of querySnapshot.docs) {
        const favoriteData = favoriteDoc.data();
        const storyDoc = await getDoc(doc(db, 'stories', favoriteData.storyId));
        
        if (storyDoc.exists()) {
          favorites.push({
            favoriteId: favoriteDoc.id,
            story: {
              id: storyDoc.id,
              ...storyDoc.data()
            }
          });
        }
      }
      
      return favorites;
    } catch (error) {
      console.error('Error fetching favorites:', error);
      toast.error('Failed to load favorites');
      throw error;
    }
  }

  static extractTags(content, placeName) {
    if (!content) return [];
    
    const words = content.toLowerCase().split(/\s+/);
    const commonWords = new Set(['the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by']);
    
    const tags = words
      .filter(word => word.length > 3 && !commonWords.has(word))
      .slice(0, 5); // Limit to 5 tags
    
    // Always include place name as a tag if available
    if (placeName) {
      const placeTag = placeName.toLowerCase().replace(/\s+/g, '-');
      tags.unshift(placeTag);
    }
    
    return [...new Set(tags)]; // Remove duplicates
  }

  static async searchStories(searchTerm, isPublicOnly = true) {
    try {
      // Note: Firestore doesn't have full-text search, so this is a basic implementation
      // For production, consider using Algolia or ElasticSearch
      const q = query(
        collection(db, 'stories'),
        ...(isPublicOnly ? [where('isPublic', '==', true)] : []),
        orderBy('createdAt', 'desc'),
        limit(50)
      );
      
      const querySnapshot = await getDocs(q);
      const stories = querySnapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      }));
      
      // Client-side filtering (not ideal for large datasets)
      const filteredStories = stories.filter(story => {
        const searchLower = searchTerm.toLowerCase();
        return (
          story.place?.name?.toLowerCase().includes(searchLower) ||
          story.content?.toLowerCase().includes(searchLower) ||
          story.title?.toLowerCase().includes(searchLower) ||
          story.tags?.some(tag => tag.includes(searchLower))
        );
      });
      
      return filteredStories;
    } catch (error) {
      console.error('Error searching stories:', error);
      toast.error('Failed to search stories');
      throw error;
    }
  }
}

export default StoryService;